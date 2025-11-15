import React, { useEffect, useRef } from 'react';
import {
  StyleSheet,
  View,
  Animated,
  ActivityIndicator,
} from 'react-native';
import { ThemedView } from '@/components/themed-view';
import { ThemedText } from '@/components/themed-text';
import { Colors } from '@/constants/theme';

interface InspectionLoadingProps {
  progress: number; // 0-100
  currentStep: string;
}

export function InspectionLoading({ progress, currentStep }: InspectionLoadingProps) {
  const colors = Colors.light;
  const progressAnim = useRef(new Animated.Value(0)).current;

  useEffect(() => {
    Animated.timing(progressAnim, {
      toValue: progress,
      duration: 300,
      useNativeDriver: false,
    }).start();
  }, [progress]);

  const widthInterpolate = progressAnim.interpolate({
    inputRange: [0, 100],
    outputRange: ['0%', '100%'],
  });

  return (
    <ThemedView style={styles.overlay}>
      <ThemedView style={[styles.container, { backgroundColor: colors.background }]}>
        {/* Icon/Spinner */}
        <View style={styles.iconContainer}>
          <ActivityIndicator size="large" color={colors.tint} />
        </View>

        {/* Title */}
        <ThemedText style={styles.title}>Processing Inspection</ThemedText>

        {/* Current Step */}
        <ThemedText style={[styles.step, { color: colors.tint }]}>
          {currentStep}
        </ThemedText>

        {/* Progress Bar */}
        <View style={[styles.progressBarContainer, { backgroundColor: colors.icon + '20' }]}>
          <Animated.View
            style={[
              styles.progressBar,
              {
                width: widthInterpolate,
                backgroundColor: colors.tint,
              },
            ]}
          />
        </View>

        {/* Progress Percentage */}
        <ThemedText style={styles.progressText}>
          {Math.round(progress)}%
        </ThemedText>
      </ThemedView>
    </ThemedView>
  );
}

const styles = StyleSheet.create({
  overlay: {
    position: 'absolute',
    top: 0,
    left: 0,
    right: 0,
    bottom: 0,
    backgroundColor: 'rgba(0, 0, 0, 0.7)',
    justifyContent: 'center',
    alignItems: 'center',
    zIndex: 1000,
  },
  container: {
    width: '85%',
    maxWidth: 400,
    borderRadius: 24,
    padding: 32,
    alignItems: 'center',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 8 },
    shadowOpacity: 0.3,
    shadowRadius: 16,
    elevation: 10,
  },
  iconContainer: {
    marginBottom: 24,
  },
  title: {
    fontSize: 24,
    fontWeight: 'bold',
    marginBottom: 12,
    textAlign: 'center',
  },
  step: {
    fontSize: 16,
    marginBottom: 24,
    textAlign: 'center',
    fontWeight: '500',
  },
  progressBarContainer: {
    width: '100%',
    height: 8,
    borderRadius: 4,
    overflow: 'hidden',
    marginBottom: 12,
  },
  progressBar: {
    height: '100%',
    borderRadius: 4,
  },
  progressText: {
    fontSize: 14,
    opacity: 0.7,
    fontWeight: '600',
  },
});

