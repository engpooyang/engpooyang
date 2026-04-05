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
          // Brand & agent
          "Porsche", "MAIA",
          // Current model lines
          "911", "718", "Taycan", "Cayenne", "Macan", "Panamera",
          // Historic models (still serviced)
          "356", "928", "944", "968", "Boxster", "Cayman",
          // 911 generation codes
          "992", "991", "997", "996", "993", "964",
          // 718/Boxster/Cayman generation codes
          "982", "981", "987", "986",
          // Panamera/Cayenne generation codes
          "970", "971", "980",
          // 911 variants
          "Carrera", "Carrera S", "Carrera 4S", "Carrera GTS",
          "Targa", "Cabriolet", "Speedster",
          // Taycan variants
          "Taycan 4S", "Taycan Turbo", "Taycan Turbo S", "Taycan Turbo GT",
          "Cross Turismo", "Sport Turismo",
          // Cayenne variants
          "Cayenne S", "Cayenne GTS", "Cayenne Turbo", "Cayenne Turbo GT",
          "Cayenne Coupe", "E-Hybrid",
          // Macan variants
          "Macan T", "Macan S", "Macan GTS", "Macan Turbo", "Macan Electric",
          // Panamera variants
          "Panamera GTS", "Panamera Turbo", "Panamera Turbo S",
          // Performance variants
          "Turbo", "Turbo S", "Turbo GT",
          "GT3", "GT3 RS", "GT2 RS", "GT4", "GT4 RS", "GTS", "S/T",
          "Spyder", "Carrera GT",
          // Transmission & drivetrain
          "PDK", "Tiptronic", "eTorque",
          // Chassis & dynamics
          "PASM", "PCCB", "PCM", "PSM", "PDCC", "PDLS", "PTV",
          "Sport Chrono", "Launch Control", "InnoDrive", "Porsche Connect",
          // Service & ownership programs
          "Tequipment", "Exclusive Manufaktur", "Porsche Classic",
          "Porsche Approved", "CPO", "PSMP", "Porsche Center",
          "Porsche Finder", "Roadside Assistance", "NHTSA",
          // Tire markings
          "N-rated", "N0", "N1", "N2",
          // Packages & trims
          "Weissach", "Weissach Package", "Heritage Design", "Sport Design",
          "Clubsport", "Lightweight", "Manthey",
          // Materials
          "Alcantara", "Nappa", "Paint to Sample",
          // Powertrain terms
          "flat-six", "twin-turbo", "T-Hybrid", "plug-in hybrid",
          "Performance Battery Plus",
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
