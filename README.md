# AI Goal Visualizer 🎯

An intelligent task prioritization tool that visualizes your goals as a solar system, with AI-powered analysis of task impact and effort.

## Features

- 🌟 **Solar System Visualization** - Your goal as the sun, tasks as planets in impact-based orbits
- 📊 **Impact/Effort Chart** - Traditional scatter plot view
- 🤖 **AI Analysis** - Smart task comparison and strategic ranking
- ⚖️ **Task Comparisons** - Understand why one task is better than another
- 🏆 **Strategic Rankings** - See where each task fits in your overall strategy

## Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure API Keys (Optional)

The app works great without API keys using smart fallback analysis. For enhanced AI analysis:

1. Copy the environment template:

   ```bash
   cp .env.example .env
   ```

2. Get API keys (choose one):
   - **Free Gemini API**: https://makersuite.google.com/app/apikey
   - **OpenAI API**: https://platform.openai.com/api-keys

3. Edit `.env` and add your key:

   ```
   GEMINI_API_KEY=your-actual-key-here
   ```

### 3. Run the App

```bash
python app.py
```

Visit `http://localhost:5000` in your browser.

## How to Use

1. **Enter your main goal** (e.g., "Get a job as a Software Engineer")
2. **List your tasks** (one per line)
3. **Click "Visualize"** to see the analysis
4. **Toggle between views** - Solar System or Impact Chart
5. **Click any planet/dot** to see detailed analysis in the side panel

## Example

**Goal**: Get a job as a Software Engineer

**Tasks**:

- Apply to 15 jobs on LinkedIn
- Build a portfolio website  
- Practice coding interviews
- Update my resume
- Attend tech meetups

The AI will analyze each task and show you why "Apply to jobs" might be higher impact than "Update resume", with detailed reasoning.

## Technology Stack

- **Backend**: Flask (Python)
- **Frontend**: HTML, CSS (Tailwind), JavaScript
- **AI**: OpenAI GPT or Google Gemini APIs
- **Visualization**: Custom solar system with GSAP animations

## Security

- API keys are stored in `.env` file (not committed to git)
- Smart fallback system works without any API keys
- No user data is stored or transmitted beyond API calls

## Contributing

Feel free to submit issues and pull requests!