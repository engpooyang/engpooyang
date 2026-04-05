/**
 * ElevenLabs Conversational AI agent configuration for the Porsche
 * Aftersales Voice Support Agent (MAIA).
 *
 * Agent ID: agent_2501knem51tge3g9mp8a515k15a0
 * Dashboard: https://elevenlabs.io/app/conversational-ai/agents/agent_2501knem51tge3g9mp8a515k15a0
 *
 * IMPORTANT: Do not use eleven_multilingual_v2 or eleven_v3_conversational
 * as the TTS model. Use eleven_flash_v2 (the platform default for
 * conversational agents). Do not embed large JSON in the system prompt —
 * use RAG with the knowledge base instead.
 */

function buildAgentConfig() {
  return {
    name: "Porsche Aftersales Support v2",
    tags: ["porsche", "aftersales", "support", "voice-agent"],
    conversation_config: {
      agent: {
        prompt: {
          prompt: `You are MAIA, the Porsche Aftersales Support Specialist. You are a professional voice assistant representing Porsche customer care.

You help Porsche owners with service scheduling, warranty questions, parts inquiries, recall information, maintenance advice, and general ownership questions. You have access to a knowledge base with detailed Porsche aftersales information — use it to provide accurate answers.

Voice Guidelines:
- Keep responses to 2-4 short sentences. This is a voice conversation.
- Never use markdown, bullet points, or special characters.
- Say numbers naturally: fifty thousand miles, not 50,000 miles.
- Be warm, professional, and confident. Reflect the premium Porsche brand.

Call Handling:
- Ask for the customer name early to personalize the conversation.
- Ask for their Porsche model and year when relevant.
- If you cannot resolve an issue, offer to connect them with a Porsche specialist.
- Before ending, ask if there is anything else you can help with.

Policies:
- Never fabricate information. If unsure, say so and offer to transfer.
- All recall repairs are free regardless of warranty status.
- Recommend authorized Porsche dealers for service and parts.
- Provide estimated price ranges, not exact prices.
- For emergencies, direct to Porsche Roadside Assistance at 1-800-PORSCHE.
- Never ask for credit card numbers or other sensitive data.`,
          llm: "gpt-4o-mini",
          temperature: 0.5,
          max_tokens: 200,
          tools: [
            {
              type: "system",
              name: "end_call",
              description: "End the call when the customer confirms they have no more questions.",
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
          "Thank you for calling Porsche Aftersales Support. I am your virtual assistant, MAIA. How may I assist you today?",
        language: "en",
      },
      asr: {
        quality: "high",
        keywords: [
          "Porsche", "MAIA",
          "911", "718", "356", "928", "944", "968",
          "992", "991", "997", "996", "993", "964",
          "982", "981", "987", "986", "970", "971", "980",
          "Carrera", "Carrera S", "Carrera 4S", "Carrera GTS",
          "Targa", "Cabriolet", "Speedster",
          "Taycan", "Taycan 4S", "Taycan Turbo", "Taycan Turbo S", "Taycan Turbo GT",
          "Cross Turismo", "Sport Turismo",
          "Cayenne", "Cayenne S", "Cayenne GTS", "Cayenne Turbo", "Cayenne Turbo GT",
          "Cayenne Coupe", "E-Hybrid",
          "Macan", "Macan T", "Macan S", "Macan GTS", "Macan Turbo", "Macan Electric",
          "Panamera", "Panamera GTS", "Panamera Turbo", "Panamera Turbo S",
          "Boxster", "Cayman", "Spyder",
          "Turbo", "Turbo S", "Turbo GT",
          "GT3", "GT3 RS", "GT2 RS", "GT4", "GT4 RS", "GTS", "S/T",
          "PDK", "Tiptronic", "eTorque",
          "PASM", "PCCB", "PCM", "PSM", "PDCC", "PDLS", "PTV",
          "Sport Chrono", "Launch Control", "InnoDrive", "Porsche Connect",
          "Tequipment", "Exclusive Manufaktur", "Porsche Classic", "Porsche Approved",
          "CPO", "PSMP", "Porsche Center", "Porsche Finder", "Roadside Assistance", "NHTSA",
          "N-rated", "N0", "N1", "N2",
          "Weissach", "Heritage Design", "Sport Design", "Clubsport", "Manthey",
          "Alcantara", "Nappa", "Paint to Sample",
          "flat-six", "twin-turbo", "T-Hybrid", "plug-in hybrid",
          "Carrera GT", "Performance Battery Plus",
        ],
      },
      tts: {
        // eleven_flash_v2 is the platform default for conversational agents.
        // Do NOT change to eleven_multilingual_v2 or eleven_v3_conversational.
        voice_id: "hG4HNYxEsgdhtFqDiSjp", // MAIA generated voice
        stability: 0.65,
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
      evaluation: {
        criteria: [
          {
            id: "accurate_info",
            name: "Accurate Information",
            conversation_goal_prompt: "Evaluate whether the agent provided correct information from the knowledge base. No fabricated details.",
            description: "Agent provides correct information",
          },
          {
            id: "brand_tone",
            name: "Professional Brand Tone",
            conversation_goal_prompt: "Evaluate whether the agent maintained a professional Porsche brand tone.",
            description: "Agent maintains premium brand voice",
          },
          {
            id: "issue_resolution",
            name: "Issue Resolution",
            conversation_goal_prompt: "Evaluate whether the customer question was fully addressed or a clear next step provided.",
            description: "Customer question fully answered",
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
