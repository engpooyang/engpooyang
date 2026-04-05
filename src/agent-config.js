/**
 * ElevenLabs Conversational AI agent configuration for the Porsche
 * Aftersales Voice Support Agent.
 */

const { buildSystemPrompt } = require('./system-prompt');
const { tools } = require('./tools');

function buildAgentConfig() {
  const systemPrompt = buildSystemPrompt();

  return {
    name: "Porsche Aftersales Support",
    tags: ["porsche", "aftersales", "support", "voice-agent"],
    conversation_config: {
      agent: {
        prompt: {
          prompt: systemPrompt,
          llm: "claude-3-5-sonnet",
          temperature: 0.4,
          max_tokens: 512,
          tools: tools,
        },
        first_message:
          "Thank you for calling Porsche Aftersales Support. My name is your Porsche virtual assistant, and I'm here to help you with any service, warranty, parts, or general questions about your Porsche. How may I assist you today?",
        language: "en",
      },
      tts: {
        voice_id: "pFZP5JQG7iQjIQuC4Bku", // "Lily" - professional, warm female voice
      },
      conversation: {
        max_duration_seconds: 600, // 10 minute max call
        client_events: [
          "conversation_initiation_metadata",
          "agent_response",
          "user_transcript",
        ],
      },
      turn: {
        mode: "turn_based",
      },
    },
    platform_settings: {
      widget: {
        variant: "compact",
        avatar: {
          type: "url",
          url: "https://upload.wikimedia.org/wikipedia/en/thumb/8/8c/Porsche_logo.svg/200px-Porsche_logo.svg.png",
        },
        feedback_mode: "during",
      },
    },
  };
}

module.exports = { buildAgentConfig };
