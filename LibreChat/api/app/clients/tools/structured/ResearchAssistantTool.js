const { DynamicTool } = require("langchain/tools");
const fetch = require("node-fetch");

class ResearchAssistantTool extends DynamicTool {
  constructor() {
    super({
      name: "research_assistant",
      description:
        "Fetch relevant research items from the research_ai_api to enhance the chatbot's responses.",
      func: async (input) => {
        try {
          const response = await fetch(
            `http://127.0.0.1:8000/find_similar_research/?query=${encodeURIComponent(input)}`
          );

          if (!response.ok) {
            throw new Error(`HTTP error! Status: ${response.status}`);
          }

          const data = await response.json();
          return JSON.stringify(data);
        } catch (error) {
          console.error("Error fetching research:", error);
          return "Error retrieving research data.";
        }
      },
    });
  }
}

module.exports = ResearchAssistantTool;
