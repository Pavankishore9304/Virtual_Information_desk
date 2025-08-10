import React from 'react';
import { StyleSheet, View, Text, SafeAreaView } from 'react-native';

export default function App() {
  return (
    <SafeAreaView style={styles.container}>
      <View style={styles.mainContent}>
        <Text style={styles.title}>VID Frontend</Text>
        <Text style={styles.subtitle}>Ready to build!</Text>
      </View>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#121212', // A dark background
  },
  mainContent: {
    flex: 1,
    alignItems: 'center',
    justifyContent: 'center',
  },
  title: {
    fontSize: 32,
    fontWeight: 'bold',
    color: '#FFFFFF',
  },
  subtitle: {
    fontSize: 18,
    color: '#AAAAAA',
    marginTop: 8,
  },
});