const { Kafka } = require('kafkajs');
const { Pool } = require('pg');

// 1. PostgreSQL Connection Setup
const pool = new Pool({
  connectionString: 'jdbc:postgresql://finalhackathonstack-postgresdb113281d2-ngpye8fmcnj7.cyvia6yge9y0.us-east-1.rds.amazonaws.com/hackathon_onprem'.replace('jdbc:', ''),
  // Agar aapka local ya EC2 wala URL hai toh yahan direct connection string bhi de sakte hain
  user: 'postgres',
  password: 'MyNewPassword123!',
  database: 'hackathon_onprem',
  host: 'finalhackathonstack-postgresdb113281d2-ngpye8fmcnj7.cyvia6yge9y0.us-east-1.rds.amazonaws.com',
  port: 5432,
});

// 2. Kafka (MSK) Connection Setup
const kafka = new Kafka({
  clientId: 'hackathon-producer',
  brokers: [
    'b-2.hackathonmskcluster.ou3kqd.c2.kafka.us-east-1.amazonaws.com:9094',
    'b-1.hackathonmskcluster.ou3kqd.c2.kafka.us-east-1.amazonaws.com:9094'
  ]
});

const producer = kafka.producer();

async function runPipeline() {
  try {
    await producer.connect();
    console.log('Connected to Kafka MSK successfully!');

    // Database se data fetch karne ki query (Aap apne table ka naam yahan change kar sakte hain)
    const dbResult = await pool.query('SELECT * FROM iot_events LIMIT 10;');
    console.log(`Fetched ${dbResult.rows.length} rows from PostgreSQL.`);

    for (const row of dbResult.rows) {
      // Har ek row ko Kafka topic par bhej rahe hain
      await producer.send({
        topic: 'kafka-topic', // ya iot-events jo bhi aapka topic ho
        messages: [
          { value: JSON.stringify(row) },
        ],
      });
      console.log(`Sent row to Kafka:`, row);
    }

    await producer.disconnect();
    await pool.end();
    console.log('Pipeline execution completed.');
  } catch (error) {
    console.error('Error in pipeline:', error);
  }
}

runPipeline();