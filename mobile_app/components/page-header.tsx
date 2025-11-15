import React from 'react';
import { View, StyleSheet, Platform } from 'react-native';
import { ThemedView } from './themed-view';
import { ThemedText } from './themed-text';
import { Colors } from '@/constants/theme';
import { useColorScheme } from '@/hooks/use-color-scheme';

interface PageHeaderProps {
  title: string;
  subtitle?: string;
}

export function PageHeader({ title, subtitle }: PageHeaderProps) {
  const colorScheme = useColorScheme();
  const colors = Colors[colorScheme ?? 'light'];

  return (
    <View style={[styles.headerContainer, { backgroundColor: colors.tint }]}>
      <ThemedView style={styles.header}>
        <ThemedText type="title" style={[styles.title, { color: '#fff' }]}>
          {title}
        </ThemedText>
        {subtitle && (
          <ThemedText style={[styles.subtitle, { color: '#ffffff90' }]}>
            {subtitle}
          </ThemedText>
        )}
      </ThemedView>
    </View>
  );
}

const styles = StyleSheet.create({
  headerContainer: {
    paddingTop: Platform.OS === 'ios' ? 70 : 50,
    paddingBottom: 24,
    borderBottomLeftRadius: 24,
    borderBottomRightRadius: 24,
    // iOS shadow
    ...(Platform.OS === 'ios' && {
      shadowColor: '#000',
      shadowOffset: { width: 0, height: 4 },
      shadowOpacity: 0.15,
      shadowRadius: 8,
    }),
    // Android elevation
    ...(Platform.OS === 'android' && {
      elevation: 8,
    }),
  },
  header: {
    paddingHorizontal: 20,
    backgroundColor: 'transparent',
  },
  title: {
    fontSize: 32,
    fontWeight: 'bold',
    marginBottom: 4,
    paddingTop: 8,
  },
  subtitle: {
    fontSize: 16,
  },
});

