import { useEffect, useRef, useState, useCallback } from 'react';

export function useWebSocket(url: string) {
  const [isConnected, setIsConnected] = useState(false);
  const [isConnecting, setIsConnecting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const wsRef = useRef<WebSocket | null>(null);
  const reconnectTimeoutRef = useRef<NodeJS.Timeout | null>(null);
  const messageHandlersRef = useRef<Set<(data: string | Blob) => void>>(new Set());

  const connect = useCallback(() => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      return;
    }

    // Close existing connection if in progress
    if (wsRef.current) {
      try {
        wsRef.current.close();
      } catch (e) {
        // Ignore errors when closing
      }
    }

    try {
      setIsConnecting(true);
      setError(null);
      console.log('Attempting to connect to WebSocket:', url);
      const ws = new WebSocket(url);
      wsRef.current = ws;

      ws.onopen = () => {
        setIsConnected(true);
        setIsConnecting(false);
        setError(null);
        console.log('WebSocket connected successfully');
      };

      ws.onmessage = (event) => {
        messageHandlersRef.current.forEach((handler) => {
          handler(event.data);
        });
      };

      ws.onclose = (event) => {
        setIsConnected(false);
        setIsConnecting(false);
        console.log('WebSocket disconnected', event.code, event.reason);
        // Only attempt to reconnect if it wasn't a manual disconnect
        if (event.code !== 1000) {
          console.log('Attempting to reconnect in 3 seconds...');
          reconnectTimeoutRef.current = setTimeout(() => {
            connect();
          }, 3000);
        }
      };

      ws.onerror = (event) => {
        setIsConnecting(false);
        console.error('WebSocket error:', event);
        setError('Connection error - check if backend server is running on port 8000');
      };
    } catch (err) {
      setIsConnecting(false);
      const errorMsg = err instanceof Error ? err.message : 'Failed to connect';
      setError(errorMsg);
      console.error('WebSocket connection error:', errorMsg);
    }
  }, [url]);

  const disconnect = useCallback(() => {
    if (reconnectTimeoutRef.current) {
      clearTimeout(reconnectTimeoutRef.current);
      reconnectTimeoutRef.current = null;
    }
    if (wsRef.current) {
      try {
        wsRef.current.close(1000, 'Manual disconnect');
      } catch (e) {
        // Ignore errors
      }
      wsRef.current = null;
    }
    setIsConnected(false);
    setIsConnecting(false);
  }, []);

  const send = useCallback((data: string | Blob) => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      wsRef.current.send(data);
      return true;
    }
    return false;
  }, []);

  const onMessage = useCallback((callback: (data: string | Blob) => void) => {
    messageHandlersRef.current.add(callback);
    return () => {
      messageHandlersRef.current.delete(callback);
    };
  }, []);

  useEffect(() => {
    connect();
    return () => {
      disconnect();
    };
  }, [connect, disconnect]);

  return {
    isConnected,
    isConnecting,
    error,
    send,
    onMessage,
    connect,
    disconnect,
  };
}
