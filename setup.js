#!/usr/bin/env node

/**
 * Porsche Aftersales Voice Agent — Setup Script
 *
 * This script provisions the ElevenLabs Conversational AI agent:
 * 1. Creates the agent with system prompt, LLM config, and tools
 * 2. Uploads knowledge base documents for RAG
 * 3. Links the knowledge base to the agent
 * 4. Lists available phone numbers for assignment
 *
 * Usage:
 *   npm run setup
 *
 * Environment:
 *   ELEVENLABS_API_KEY — your ElevenLabs API key (set in .env)
 */

require('dotenv').config();

const { buildAgentConfig } = require('./src/agent-config');
const { loadKnowledge } = require('./src/system-prompt');
const path = require('path');
const fs = require('fs');

const API_BASE = 'https://api.elevenlabs.io/v1';
const API_KEY = process.env.ELEVENLABS_API_KEY;

if (!API_KEY) {
  console.error('Error: ELEVENLABS_API_KEY is not set. Copy .env.example to .env and add your key.');
  process.exit(1);
}

const headers = {
  'xi-api-key': API_KEY,
  'Content-Type': 'application/json',
};

// ─── Helpers ───────────────────────────────────────────────────────────────

async function apiRequest(method, endpoint, body) {
  const url = `${API_BASE}${endpoint}`;
  const options = { method, headers };

  if (body) {
    options.body = JSON.stringify(body);
  }

  const response = await fetch(url, options);

  if (!response.ok) {
    const errorText = await response.text();
    throw new Error(`API ${method} ${endpoint} failed (${response.status}): ${errorText}`);
  }

  const text = await response.text();
  return text ? JSON.parse(text) : null;
}

// ─── Step 1: Create Agent ──────────────────────────────────────────────────

async function createAgent() {
  console.log('\n[1/4] Creating Porsche Aftersales Support agent...');

  const config = buildAgentConfig();

  const result = await apiRequest('POST', '/convai/agents/create', config);
  const agentId = result.agent_id;

  console.log(`      Agent created successfully!`);
  console.log(`      Agent ID: ${agentId}`);

  return agentId;
}

// ─── Step 2: Upload Knowledge Base ─────────────────────────────────────────

async function uploadKnowledgeBase() {
  console.log('\n[2/4] Uploading knowledge base documents...');

  const knowledgeDir = path.join(__dirname, 'src', 'knowledge');
  const files = [
    { file: 'services.json', name: 'Porsche Service Intervals & Maintenance' },
    { file: 'warranty.json', name: 'Porsche Warranty Information' },
    { file: 'parts.json', name: 'Porsche Parts Catalog' },
    { file: 'recalls.json', name: 'Porsche Active Recalls' },
    { file: 'faq.json', name: 'Porsche Aftersales FAQ' },
  ];

  const documentIds = [];

  for (const { file, name } of files) {
    const filePath = path.join(knowledgeDir, file);
    const content = fs.readFileSync(filePath, 'utf-8');

    const result = await apiRequest('POST', '/convai/knowledge-base/text', {
      text: content,
      name: name,
    });

    console.log(`      Uploaded: ${name} (ID: ${result.id})`);
    documentIds.push(result.id);
  }

  return documentIds;
}

// ─── Step 3: Link Knowledge Base to Agent ──────────────────────────────────

async function linkKnowledgeBase(agentId, documentIds) {
  console.log('\n[3/4] Linking knowledge base to agent...');

  const knowledgeBase = documentIds.map((id) => ({
    type: 'text',
    id: id,
  }));

  await apiRequest('PATCH', `/convai/agents/${agentId}`, {
    conversation_config: {
      agent: {
        prompt: {
          knowledge_base: knowledgeBase,
        },
      },
    },
  });

  console.log(`      Linked ${documentIds.length} documents to agent.`);
}

// ─── Step 4: Phone Number Setup ────────────────────────────────────────────

async function setupPhoneNumber(agentId) {
  console.log('\n[4/4] Checking phone number configuration...');

  try {
    const result = await apiRequest('GET', '/convai/phone-numbers');
    const phoneNumbers = Array.isArray(result) ? result : (result.phone_numbers || []);

    if (phoneNumbers.length === 0) {
      console.log('      No phone numbers found on your account.');
      console.log('      To enable phone support:');
      console.log('        1. Go to ElevenLabs Dashboard > Conversational AI > Phone Numbers');
      console.log('        2. Add a phone number (Twilio or SIP Trunk)');
      console.log(`        3. Assign it to agent ID: ${agentId}`);
      console.log('      See docs/phone-setup.md for detailed instructions.');
      return null;
    }

    // Find an unassigned inbound-capable number, or list all
    const available = phoneNumbers.filter((p) => !p.agent_id);
    if (available.length > 0) {
      const phone = available[0];
      const phoneId = phone.phone_number_id || phone.id;

      await apiRequest('PATCH', `/convai/phone-numbers/${phoneId}`, {
        agent_id: agentId,
      });

      const number = phone.phone_number || phone.label || phoneId;
      console.log(`      Assigned phone number: ${number}`);
      console.log(`      Customers can now call this number to reach the Porsche support agent.`);
      return number;
    } else {
      console.log('      All phone numbers are already assigned to other agents.');
      console.log('      Available phone numbers:');
      for (const p of phoneNumbers) {
        const num = p.phone_number || p.label || p.phone_number_id;
        console.log(`        - ${num} (assigned to agent: ${p.agent_id})`);
      }
      console.log(`\n      To reassign, update a phone number to agent ID: ${agentId}`);
      return null;
    }
  } catch (err) {
    console.log(`      Phone number setup skipped: ${err.message}`);
    console.log('      You can configure phone numbers manually in the ElevenLabs dashboard.');
    return null;
  }
}

// ─── Main ──────────────────────────────────────────────────────────────────

async function main() {
  console.log('='.repeat(60));
  console.log('  Porsche Aftersales Voice Support Agent — Setup');
  console.log('='.repeat(60));

  try {
    const agentId = await createAgent();
    const documentIds = await uploadKnowledgeBase();
    await linkKnowledgeBase(agentId, documentIds);
    const phoneNumber = await setupPhoneNumber(agentId);

    console.log('\n' + '='.repeat(60));
    console.log('  Setup Complete!');
    console.log('='.repeat(60));
    console.log(`\n  Agent ID:     ${agentId}`);
    console.log(`  Dashboard:    https://elevenlabs.io/app/conversational-ai/agents/${agentId}`);
    if (phoneNumber) {
      console.log(`  Phone Number: ${phoneNumber}`);
    }
    console.log(`\n  Next steps:`);
    console.log(`    1. Visit the dashboard link above to test the agent`);
    console.log(`    2. Use the widget or phone to have a voice conversation`);
    console.log(`    3. Review conversation logs in the ElevenLabs dashboard`);
    if (!phoneNumber) {
      console.log(`    4. Set up a phone number — see docs/phone-setup.md`);
    }
    console.log('');
  } catch (err) {
    console.error(`\nSetup failed: ${err.message}`);
    process.exit(1);
  }
}

main();
