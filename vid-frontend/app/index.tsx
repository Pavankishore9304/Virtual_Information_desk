import React, { useState, useEffect, useRef } from 'react';
import { StyleSheet, View, Text, TextInput, TouchableOpacity, SafeAreaView, FlatList, KeyboardAvoidingView, Platform, ActivityIndicator } from 'react-native';
import { LinearGradient } from 'expo-linear-gradient';
import { StatusBar } from 'expo-status-bar';

export default function Page() {
  const [chats, setChats] = useState({});
  const [currentSessionId, setCurrentSessionId] = useState(null);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const flatListRef = useRef(null);

  const startNewChat = async () => {
    setIsLoading(true);
    try {
      const response = await fetch('http://10.147.197.208:8000/start', { method: 'POST' });
      const data = await response.json();
      const newSessionId = data.session_id;
      setChats(prev => ({
        ...prev,
        [newSessionId]: [{ id: '1', text: 'Hello! How can I assist you today?', sender: 'ai' }]
      }));
      setCurrentSessionId(newSessionId);
    } catch (error) {
      console.error("Failed to start new chat:", error);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    startNewChat();
  }, []);

  useEffect(() => {
    if (flatListRef.current) {
      flatListRef.current.scrollToEnd({ animated: true });
    }
  }, [chats, currentSessionId]);

  const handleSend = async () => {
    if (input.trim().length === 0 || isLoading || !currentSessionId) return;

    const userMessage = { id: Date.now().toString(), text: input, sender: 'user' };
    const updatedMessages = [...chats[currentSessionId], userMessage];
    setChats(prev => ({ ...prev, [currentSessionId]: updatedMessages }));
    setInput('');
    setIsLoading(true);

    try {
      const response = await fetch('http://10.147.197.208:8000/ask', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query: input, session_id: currentSessionId }),
      });

      if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);

      const data = await response.json();
      const aiMessage = { id: Date.now().toString(), text: data.response, sender: 'ai' };
      setChats(prev => ({ ...prev, [currentSessionId]: [...updatedMessages, aiMessage] }));

    } catch (error) {
      console.error("Failed to fetch from backend:", error);
      const errorMessage = { id: Date.now().toString(), text: "Sorry, I'm having trouble connecting. Please try again later.", sender: 'ai' };
      setChats(prev => ({ ...prev, [currentSessionId]: [...updatedMessages, errorMessage] }));
    } finally {
      setIsLoading(false);
    }
  };

  const renderMessage = ({ item }) => (
    <View style={[
      styles.messageBubble,
      item.sender === 'user' ? styles.userMessage : styles.aiMessage
    ]}>
      <Text style={styles.messageText}>{item.text}</Text>
    </View>
  );

  const currentMessages = chats[currentSessionId] || [];

  return (
    <LinearGradient
      colors={['#1c1c2e', '#3c3c5e']}
      style={styles.container}
    >
      <StatusBar style="light" />
      <SafeAreaView style={styles.flexContainer}>
        <View style={styles.header}>
          <Text style={styles.headerTitle}>Virtual Assistant</Text>
          <TouchableOpacity onPress={startNewChat} style={styles.newChatButton}>
            <Text style={styles.newChatButtonText}>+</Text>
          </TouchableOpacity>
        </View>
        <KeyboardAvoidingView
          behavior={Platform.OS === "ios" ? "padding" : "height"}
          style={styles.flexContainer}
          keyboardVerticalOffset={Platform.OS === "ios" ? 60 : 0}
        >
          <FlatList
            ref={flatListRef}
            data={currentMessages}
            renderItem={renderMessage}
            keyExtractor={item => item.id}
            style={styles.chatHistory}
            contentContainerStyle={{ paddingHorizontal: 15, paddingTop: 20, paddingBottom: 10 }}
          />
          <View style={styles.inputContainer}>
            <TextInput
              style={styles.textInput}
              value={input}
              onChangeText={setInput}
              placeholder="Start typing..."
              placeholderTextColor="#999"
              editable={!isLoading}
            />
            <TouchableOpacity style={styles.sendButton} onPress={handleSend} disabled={isLoading}>
              {isLoading ? <ActivityIndicator size="small" color="#fff" /> : <Text style={styles.sendButtonText}>➤</Text>}
            </TouchableOpacity>
          </View>
        </KeyboardAvoidingView>
      </SafeAreaView>
    </LinearGradient>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1 },
  flexContainer: { flex: 1 },
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingHorizontal: 15,
    paddingVertical: 10,
    paddingTop: Platform.OS === 'android' ? 40 : 20,
    borderBottomWidth: 1,
    borderBottomColor: 'rgba(255, 255, 255, 0.1)',
  },
  newChatButton: {
    backgroundColor: '#007AFF',
    borderRadius: 15,
    width: 30,
    height: 30,
    justifyContent: 'center',
    alignItems: 'center',
  },
  newChatButtonText: {
    color: 'white',
    fontSize: 20,
    fontWeight: 'bold',
  },
  headerTitle: {
    color: 'white',
    fontSize: 20,
    fontWeight: 'bold',
  },
  chatHistory: { flex: 1 },
  messageBubble: {
    paddingVertical: 12,
    paddingHorizontal: 18,
    borderRadius: 25,
    marginBottom: 12,
    maxWidth: '80%',
    elevation: 3,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.2,
    shadowRadius: 2,
  },
  userMessage: {
    backgroundColor: '#007AFF',
    alignSelf: 'flex-end',
    borderBottomRightRadius: 5,
  },
  aiMessage: {
    backgroundColor: '#4E4E5A',
    alignSelf: 'flex-start',
    borderBottomLeftRadius: 5,
  },
  messageText: {
    color: 'white',
    fontSize: 16,
  },
  inputContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingHorizontal: 12,
    paddingVertical: 8,
    paddingBottom: Platform.OS === 'ios' ? 20 : 8,
    borderTopWidth: 1,
    borderTopColor: 'rgba(255,255,255,0.1)',
    backgroundColor: 'rgba(0,0,0,0.2)'
  },
  textInput: {
    flex: 1,
    backgroundColor: '#3e3e50',
    borderRadius: 25,
    paddingHorizontal: 20,
    paddingVertical: 12,
    color: 'white',
    marginRight: 10,
    fontSize: 16,
  },
  sendButton: {
    backgroundColor: '#007AFF',
    borderRadius: 25,
    width: 50,
    height: 50,
    justifyContent: 'center',
    alignItems: 'center',
  },
  sendButtonText: {
    color: '#fff',
    fontSize: 24,
    lineHeight: 28,
  },
});
