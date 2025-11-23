# African health studio - Next.js Frontend

Modern Next.js frontend for the African health studio application with webcam and audio recording capabilities.

## Features

- 🎥 **Webcam Integration** - Real-time video feed with mirror effect
- 🎤 **Audio Recording** - Real-time audio capture and streaming
- 📊 **Audio Visualization** - Live waveform visualization
- 💬 **Conversation Log** - Real-time chat interface
- 🔌 **WebSocket Connection** - Real-time communication with backend
- 🎨 **Modern UI** - Beautiful dark theme with Tailwind CSS

## Setup

1. Install dependencies:
```bash
npm install
# or
yarn install
# or
pnpm install
```

2. Make sure your backend server is running on port 8000 (or update the WebSocket URL in `app/page.tsx`)

3. Run the development server:
```bash
npm run dev
# or
yarn dev
# or
pnpm dev
```

4. Open [http://localhost:3000](http://localhost:3000) in your browser

## Project Structure

```
frontend-next/
├── app/
│   ├── components/       # React components
│   │   ├── AudioVisualizer.tsx
│   │   ├── ChatMessage.tsx
│   │   ├── ConversationLog.tsx
│   │   ├── ControlButtons.tsx
│   │   └── WebcamView.tsx
│   ├── hooks/           # Custom React hooks
│   │   ├── useMediaStream.ts
│   │   └── useWebSocket.ts
│   ├── globals.css      # Global styles
│   ├── layout.tsx       # Root layout
│   └── page.tsx         # Main page
├── public/              # Static files
└── package.json
```

## Configuration

The frontend connects to the backend WebSocket at `ws://localhost:8000/ws/audio` by default. You can modify this in `app/page.tsx`:

```typescript
const wsProtocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
const wsHost = window.location.hostname;
const wsPort = '8000';
const wsUrl = `${wsProtocol}//${wsHost}:${wsPort}/ws/audio`;
```

## Building for Production

```bash
npm run build
npm start
```

