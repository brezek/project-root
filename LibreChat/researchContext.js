const axios = require('axios');

const getResearchContext = async (req, res, next) => {
  try {
    const projectId = req.headers['x-project-id'];
    if (!projectId) {
      return next();
    }

    // Connect to your FastAPI backend
    const response = await axios.get(`http://localhost:8000/chat_context/${projectId}`);
    
    // Attach research context to the request
    req.researchContext = response.data;
    next();
  } catch (error) {
    console.error('Error fetching research context:', error);
    next();
  }
};

module.exports = getResearchContext;