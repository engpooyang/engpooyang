/**
 * Tool definitions for the Porsche Aftersales Voice Agent.
 *
 * These are registered as "server tools" in ElevenLabs. When the LLM decides
 * to call one, ElevenLabs sends a webhook to our tool server endpoint (or
 * resolves them inline if using the dashboard-hosted knowledge base).
 *
 * For the initial POC the tools reference the static knowledge base so the
 * agent can surface specific data during conversation.
 */

const tools = [
  {
    type: "webhook",
    name: "lookup_service_schedule",
    description:
      "Look up the recommended service schedule and maintenance intervals for a specific Porsche model. Call this when a customer asks about service intervals, next service due, or maintenance schedule.",
    parameters: {
      type: "object",
      properties: {
        model: {
          type: "string",
          description:
            "The Porsche model name, for example: 911, Cayenne, Taycan, Macan, Panamera, or 718",
        },
        service_type: {
          type: "string",
          enum: ["minor", "major", "brake_fluid"],
          description:
            "The type of service to look up. Minor is routine maintenance, major is comprehensive service, brake_fluid is the brake fluid flush interval.",
        },
      },
      required: ["model"],
    },
  },
  {
    type: "webhook",
    name: "check_warranty_coverage",
    description:
      "Check warranty coverage details for a Porsche vehicle. Call this when a customer asks about their warranty status, what is covered, or warranty options.",
    parameters: {
      type: "object",
      properties: {
        warranty_type: {
          type: "string",
          enum: [
            "new_vehicle",
            "cpo",
            "extended",
            "corrosion",
            "emissions",
            "hybrid_ev_battery",
          ],
          description:
            "The type of warranty to look up. Use new_vehicle for standard factory warranty, cpo for Certified Pre-Owned, extended for extended warranty plans.",
        },
      },
      required: ["warranty_type"],
    },
  },
  {
    type: "webhook",
    name: "search_parts_catalog",
    description:
      "Search the Porsche parts catalog for specific parts information, pricing, and availability. Call this when a customer asks about replacement parts, prices, or ordering.",
    parameters: {
      type: "object",
      properties: {
        category: {
          type: "string",
          enum: ["brakes", "filters", "fluids", "tires", "electrical"],
          description: "The parts category to search.",
        },
        model: {
          type: "string",
          description:
            "The Porsche model to filter parts for, for example: 911, Cayenne, Taycan.",
        },
      },
      required: ["category"],
    },
  },
  {
    type: "webhook",
    name: "check_active_recalls",
    description:
      "Check for active recalls affecting a specific Porsche model. Call this when a customer asks about recalls, safety campaigns, or whether their vehicle is affected.",
    parameters: {
      type: "object",
      properties: {
        model: {
          type: "string",
          description:
            "The Porsche model to check recalls for, for example: 911, Cayenne, Taycan, Macan.",
        },
        year: {
          type: "string",
          description:
            "The model year to check, for example: 2023 or 2024.",
        },
      },
      required: ["model"],
    },
  },
  {
    type: "webhook",
    name: "schedule_service_appointment",
    description:
      "Collect customer information to schedule a service appointment at their preferred Porsche dealer. Call this when a customer wants to book a service appointment.",
    parameters: {
      type: "object",
      properties: {
        customer_name: {
          type: "string",
          description: "The customer's full name.",
        },
        model: {
          type: "string",
          description:
            "The Porsche model, for example: 911 Carrera, Cayenne Turbo.",
        },
        year: {
          type: "string",
          description: "The model year of the vehicle.",
        },
        service_type: {
          type: "string",
          description:
            "The type of service needed, for example: routine maintenance, brake service, recall repair.",
        },
        preferred_date: {
          type: "string",
          description:
            "The customer's preferred appointment date.",
        },
        preferred_dealer: {
          type: "string",
          description:
            "The customer's preferred Porsche dealer location or city.",
        },
      },
      required: ["customer_name", "model", "service_type"],
    },
  },
  {
    type: "webhook",
    name: "transfer_to_specialist",
    description:
      "Transfer the call to a human Porsche specialist. Use this when the customer's issue requires human assistance, when you cannot resolve the inquiry, or when the customer specifically requests to speak with a person.",
    parameters: {
      type: "object",
      properties: {
        reason: {
          type: "string",
          description:
            "A brief summary of why the transfer is needed and what the customer needs help with.",
        },
        department: {
          type: "string",
          enum: ["service", "parts", "warranty", "general"],
          description: "The department to transfer the call to.",
        },
      },
      required: ["reason", "department"],
    },
  },
];

module.exports = { tools };
