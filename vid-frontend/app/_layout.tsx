// Put this configuration at the very top of the file.
import { LogBox } from 'react-native';
LogBox.ignoreLogs([
  "EXGL: gl.pixelStorei() doesn't support this parameter yet!"
]);

import { Stack } from 'expo-router';
import React from 'react';

export default function RootLayout() {
  return (
    <Stack>
      <Stack.Screen name="index" options={{ headerShown: false }} />
    </Stack>
  );
}