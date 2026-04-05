/**
 * ElevenLabs Workflow definition for the Porsche Aftersales Voice Agent.
 *
 * Flow:
 *   Start → Intent Router → [Service|Warranty|Parts|Recalls|General] → Resolution → End/Transfer/Loop
 *
 * Node types:
 *   - start: Entry point
 *   - override_agent: Modifies base agent with department-specific system prompt
 *   - end: Graceful call termination
 *
 * Edge conditions use LLM-based routing to detect customer intent.
 */

function buildWorkflow() {
  function overrideAgent(id, label, prompt, x, y, edges) {
    return {
      id,
      type: "override_agent",
      label,
      position: { x, y },
      edge_order: edges,
      override_agent: {
        conversation_config: {
          agent: { prompt: { prompt } },
        },
      },
    };
  }

  const nodes = {
    start_node: {
      id: "start_node",
      type: "start",
      label: "Start",
      position: { x: 0, y: 300 },
      edge_order: ["start_to_router"],
      start: {},
    },

    // Intent Router — classifies customer need
    ...Object.fromEntries(
      [
        overrideAgent(
          "router",
          "Intent Router",
          "You are MAIA, a Porsche Aftersales routing specialist. Understand what the customer needs and route them. Ask one clarifying question if needed. Categories: service and maintenance, warranty coverage, parts inquiries, recall information, or general questions.",
          400,
          300,
          [
            "route_service",
            "route_warranty",
            "route_parts",
            "route_recalls",
            "route_general",
          ]
        ),

        // Department specialists
        overrideAgent(
          "service_agent",
          "Service Specialist",
          "You are MAIA, specializing in Porsche service and maintenance. Help with scheduling, maintenance intervals, service details, and estimated costs. Ask for the Porsche model and year. Use the knowledge base. Keep responses to two to four sentences.",
          800,
          0,
          ["service_to_resolution"]
        ),
        overrideAgent(
          "warranty_agent",
          "Warranty Specialist",
          "You are MAIA, specializing in Porsche warranty coverage. Help with warranty status, coverage details, claims guidance, and extended warranty options. Ask for model, year, and mileage. Use the knowledge base.",
          800,
          150,
          ["warranty_to_resolution"]
        ),
        overrideAgent(
          "parts_agent",
          "Parts Specialist",
          "You are MAIA, specializing in Porsche genuine parts. Help with finding parts, pricing ranges, OEM vs aftermarket, and ordering. Always recommend genuine Porsche parts. Use the knowledge base.",
          800,
          300,
          ["parts_to_resolution"]
        ),
        overrideAgent(
          "recalls_agent",
          "Recalls Specialist",
          "You are MAIA, specializing in Porsche recall information. Help check active recalls, explain coverage, and guide scheduling. All recall repairs are free regardless of warranty status. Use the knowledge base.",
          800,
          450,
          ["recalls_to_resolution"]
        ),
        overrideAgent(
          "general_agent",
          "General Support",
          "You are MAIA, a general Porsche aftersales assistant. Help with Porsche Connect, roadside assistance at 1-800-PORSCHE, dealer locations, CPO program, and ownership questions. Use the knowledge base FAQ.",
          800,
          600,
          ["general_to_resolution"]
        ),

        // Resolution check — loop or end
        overrideAgent(
          "resolution",
          "Resolution Check",
          "You are MAIA. Ask if there is anything else you can help with today. If they have another question, let them know you are happy to help. If satisfied, thank them warmly for choosing Porsche.",
          1200,
          300,
          ["to_end", "to_transfer", "back_to_router"]
        ),
      ].map((n) => [n.id, n])
    ),

    // End nodes
    transfer_end: {
      id: "transfer_end",
      type: "end",
      label: "Transfer to Human",
      position: { x: 1600, y: 450 },
      edge_order: [],
      end: {},
    },
    goodbye: {
      id: "goodbye",
      type: "end",
      label: "End Call",
      position: { x: 1600, y: 150 },
      edge_order: [],
      end: {},
    },
  };

  const edges = {
    // Start → Router
    start_to_router: {
      source: "start_node",
      target: "router",
      forward_condition: { type: "unconditional" },
    },

    // Router → Department specialists (LLM-based intent detection)
    route_service: {
      source: "router",
      target: "service_agent",
      forward_condition: {
        type: "llm",
        condition:
          "Customer wants help with service scheduling, maintenance, oil changes, brake service, or vehicle servicing.",
      },
    },
    route_warranty: {
      source: "router",
      target: "warranty_agent",
      forward_condition: {
        type: "llm",
        condition:
          "Customer wants help with warranty coverage, claims, extended warranty, or CPO warranty.",
      },
    },
    route_parts: {
      source: "router",
      target: "parts_agent",
      forward_condition: {
        type: "llm",
        condition:
          "Customer wants help with replacement parts, ordering, pricing, brake pads, filters, or tires.",
      },
    },
    route_recalls: {
      source: "router",
      target: "recalls_agent",
      forward_condition: {
        type: "llm",
        condition:
          "Customer wants to check recalls, safety campaigns, or schedule recall repairs.",
      },
    },
    route_general: {
      source: "router",
      target: "general_agent",
      forward_condition: {
        type: "llm",
        condition:
          "Customer has a general question not about service, warranty, parts, or recalls.",
      },
    },

    // Specialists → Resolution
    service_to_resolution: {
      source: "service_agent",
      target: "resolution",
      forward_condition: {
        type: "llm",
        condition: "Service inquiry addressed and customer seems satisfied.",
      },
    },
    warranty_to_resolution: {
      source: "warranty_agent",
      target: "resolution",
      forward_condition: {
        type: "llm",
        condition: "Warranty inquiry addressed and customer seems satisfied.",
      },
    },
    parts_to_resolution: {
      source: "parts_agent",
      target: "resolution",
      forward_condition: {
        type: "llm",
        condition: "Parts inquiry addressed and customer seems satisfied.",
      },
    },
    recalls_to_resolution: {
      source: "recalls_agent",
      target: "resolution",
      forward_condition: {
        type: "llm",
        condition: "Recall inquiry addressed and customer seems satisfied.",
      },
    },
    general_to_resolution: {
      source: "general_agent",
      target: "resolution",
      forward_condition: {
        type: "llm",
        condition: "General inquiry addressed and customer seems satisfied.",
      },
    },

    // Resolution → End / Transfer / Loop
    to_end: {
      source: "resolution",
      target: "goodbye",
      forward_condition: {
        type: "llm",
        condition:
          "Customer confirms no more questions and wants to end the call.",
      },
    },
    to_transfer: {
      source: "resolution",
      target: "transfer_end",
      forward_condition: {
        type: "llm",
        condition:
          "Customer requests a human specialist or issue needs human intervention.",
      },
    },
    back_to_router: {
      source: "resolution",
      target: "router",
      forward_condition: {
        type: "llm",
        condition: "Customer has another question or different topic.",
      },
    },
  };

  return { nodes, edges };
}

module.exports = { buildWorkflow };
