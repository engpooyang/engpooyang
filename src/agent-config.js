/**
 * ElevenLabs Conversational AI agent configuration for the Porsche
 * Aftersales Voice Support Agent (MAIA).
 *
 * This config mirrors what is deployed in ElevenLabs. The setup.js script
 * uses this to create/update the agent via the API.
 */

const { buildSystemPrompt } = require('./system-prompt');

function buildAgentConfig() {
  const systemPrompt = buildSystemPrompt();

  return {
    name: "Porsche Aftersales Support",
    tags: ["porsche", "aftersales", "support", "voice-agent"],
    conversation_config: {
      agent: {
        prompt: {
          prompt: systemPrompt,
          llm: "gpt-oss-120b",
          temperature: 0.4,
          max_tokens: 512,
          tools: [
            {
              type: "system",
              name: "end_call",
              description: "End the phone call when the customer confirms they have no more questions.",
            },
            {
              type: "system",
              name: "language_detection",
              description: "Detect the language the customer is speaking and switch to that language.",
            },
          ],
          rag: {
            enabled: true,
            max_retrieved_rag_chunks_count: 12,
          },
        },
        first_message:
          "Thank you for calling Porsche Aftersales Support. I'm your Porsche virtual assistant, MAIA. How may I assist you today?",
        language: "en",
      },
      asr: {
        quality: "high",
        provider: "scribe_realtime",
        keywords: [
          "Porsche", "Cayenne", "Taycan", "Macan", "Panamera", "Carrera",
          "Targa", "Turbo", "PCCB", "PDK", "PASM", "PCM", "PSM",
          "Tequipment", "N-rated", "CPO", "Boxster", "Cayman",
          "GT3", "GT4", "GTS", "Turbo S", "MAIA", "992", "718",
        ],
      },
      tts: {
        voice_id: "hG4HNYxEsgdhtFqDiSjp",
        stability: 0.65,
        expressive_mode: true,
      },
      conversation: {
        max_duration_seconds: 600,
        client_events: [
          "conversation_initiation_metadata",
          "agent_response",
          "user_transcript",
        ],
      },
      turn: {
        mode: "turn",
        turn_timeout: 10.0,
        silence_end_call_timeout: 30.0,
        turn_eagerness: "patient",
        soft_timeout_config: {
          timeout_seconds: 3.5,
          use_llm_generated_message: true,
        },
      },
    },
    platform_settings: {
      guardrails: {
        version: "1",
        focus: { is_enabled: true },
        prompt_injection: { is_enabled: true },
        content: {
          execution_mode: "blocking",
          config: {
            profanity: { is_enabled: true, threshold: "medium" },
            harassment: { is_enabled: true, threshold: "medium" },
            violence: { is_enabled: true, threshold: "medium" },
            self_harm: { is_enabled: true, threshold: "medium" },
          },
          trigger_action: { type: "retry" },
        },
      },
      evaluation: {
        criteria: [
          {
            id: "accurate_info",
            name: "Accurate Information",
            conversation_goal_prompt: "Evaluate whether the agent provided correct information from the knowledge base. No fabricated details.",
          },
          {
            id: "brand_tone",
            name: "Professional Brand Tone",
            conversation_goal_prompt: "Evaluate whether the agent maintained a professional, courteous Porsche brand tone.",
          },
          {
            id: "issue_resolution",
            name: "Issue Resolution",
            conversation_goal_prompt: "Evaluate whether the customer question was fully addressed or a clear next step provided.",
          },
          {
            id: "appropriate_escalation",
            name: "Appropriate Escalation",
            conversation_goal_prompt: "Evaluate whether the agent correctly offered to transfer to a specialist when needed.",
          },
        ],
      },
      widget: {
        variant: "compact",
        feedback_mode: "during",
      },
    },
  };
}

module.exports = { buildAgentConfig };
