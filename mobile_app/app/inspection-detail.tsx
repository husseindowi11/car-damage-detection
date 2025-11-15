import React, { useEffect, useState } from 'react';
import {
  StyleSheet,
  ScrollView,
  ActivityIndicator,
  Alert,
  View,
} from 'react-native';
import { useLocalSearchParams, useRouter } from 'expo-router';
import { ThemedView } from '@/components/themed-view';
import { ThemedText } from '@/components/themed-text';
import { Colors } from '@/constants/theme';
import { useColorScheme } from '@/hooks/use-color-scheme';
import { getInspectionDetails } from '@/services/api';
import { getImageUrl } from '@/config/api';
import type { InspectionDetail, DamageItem } from '@/types/api';
import { Image } from 'expo-image';

export default function InspectionDetailScreen() {
  const { id } = useLocalSearchParams<{ id: string }>();
  const router = useRouter();
  const colorScheme = useColorScheme();
  const [inspection, setInspection] = useState<InspectionDetail | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (id) {
      loadInspectionDetails();
    }
  }, [id]);

  const loadInspectionDetails = async () => {
    try {
      setLoading(true);
      const response = await getInspectionDetails(id!);
      if (response.status && response.data) {
        setInspection(response.data);
      }
    } catch (error: any) {
      Alert.alert(
        'Error',
        error.response?.data?.message || 'Failed to load inspection details'
      );
      router.back();
    } finally {
      setLoading(false);
    }
  };

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
    }).format(amount);
  };

  const getSeverityColor = (severity: string) => {
    switch (severity.toLowerCase()) {
      case 'minor':
        return '#10B981'; // green
      case 'moderate':
        return '#F59E0B'; // amber
      case 'major':
        return '#EF4444'; // red
      default:
        return '#6B7280'; // gray
    }
  };

  const colors = Colors[colorScheme ?? 'light'];

  if (loading) {
    return (
      <ThemedView style={styles.container}>
        <ActivityIndicator size="large" color={colors.tint} />
        <ThemedText style={styles.loadingText}>Loading...</ThemedText>
      </ThemedView>
    );
  }

  if (!inspection) {
    return (
      <ThemedView style={styles.container}>
        <ThemedText>Inspection not found</ThemedText>
      </ThemedView>
    );
  }

  return (
    <ThemedView style={styles.container}>
      <ScrollView
        style={styles.scrollView}
        contentContainerStyle={styles.scrollContent}
        showsVerticalScrollIndicator={false}
      >
        {/* Header */}
        <ThemedView style={styles.header}>
          <ThemedText type="title" style={styles.title}>
            {inspection.car_name}
          </ThemedText>
          <ThemedText style={styles.subtitle}>
            {inspection.car_model} • {inspection.car_year}
          </ThemedText>
          <ThemedText style={styles.date}>
            {formatDate(inspection.created_at)}
          </ThemedText>
        </ThemedView>

        {/* Total Cost Card */}
        <ThemedView style={[styles.card, { backgroundColor: colors.background }]}>
          <ThemedText style={styles.cardLabel}>Total Estimated Cost</ThemedText>
          <ThemedText style={[styles.totalCost, { color: colors.tint }]}>
            {formatCurrency(inspection.total_damage_cost)}
          </ThemedText>
        </ThemedView>

        {/* Summary */}
        <ThemedView style={[styles.card, { backgroundColor: colors.background }]}>
          <ThemedText style={styles.cardTitle}>Summary</ThemedText>
          <ThemedText style={styles.summaryText}>
            {inspection.damage_report.summary}
          </ThemedText>
        </ThemedView>

        {/* Damage Items */}
        {inspection.damage_report.new_damage.length > 0 && (
          <ThemedView style={styles.section}>
            <ThemedText style={styles.sectionTitle}>Damage Details</ThemedText>
            {inspection.damage_report.new_damage.map((damage: DamageItem, index: number) => (
              <ThemedView
                key={index}
                style={[styles.damageCard, { backgroundColor: colors.background }]}
              >
                <ThemedView style={styles.damageHeader}>
                  <ThemedText style={styles.damagePart}>{damage.car_part}</ThemedText>
                  <View
                    style={[
                      styles.severityBadge,
                      { backgroundColor: getSeverityColor(damage.severity) + '20' },
                    ]}
                  >
                    <ThemedText
                      style={[
                        styles.severityText,
                        { color: getSeverityColor(damage.severity) },
                      ]}
                    >
                      {damage.severity.toUpperCase()}
                    </ThemedText>
                  </View>
                </ThemedView>
                
                <ThemedText style={styles.damageType}>{damage.damage_type}</ThemedText>
                <ThemedText style={styles.damageDescription}>{damage.description}</ThemedText>
                
                <ThemedView style={styles.damageFooter}>
                  <ThemedText style={styles.damageAction}>
                    Action: {damage.recommended_action}
                  </ThemedText>
                  <ThemedText style={[styles.damageCost, { color: colors.tint }]}>
                    {formatCurrency(damage.estimated_cost_usd)}
                  </ThemedText>
                </ThemedView>
              </ThemedView>
            ))}
          </ThemedView>
        )}

        {/* Images Section */}
        {(inspection.before_images.length > 0 || inspection.after_images.length > 0) && (
          <ThemedView style={styles.section}>
            <ThemedText style={styles.sectionTitle}>Images</ThemedText>
            
            {inspection.before_images.length > 0 && (
              <ThemedView style={styles.imageSection}>
                <ThemedText style={styles.imageSectionTitle}>Before</ThemedText>
                <ScrollView horizontal showsHorizontalScrollIndicator={false}>
                  {inspection.before_images.map((imagePath, index) => (
                    <Image
                      key={index}
                      source={{ uri: getImageUrl(imagePath) }}
                      style={styles.image}
                      contentFit="cover"
                    />
                  ))}
                </ScrollView>
              </ThemedView>
            )}

            {inspection.after_images.length > 0 && (
              <ThemedView style={styles.imageSection}>
                <ThemedText style={styles.imageSectionTitle}>After</ThemedText>
                <ScrollView horizontal showsHorizontalScrollIndicator={false}>
                  {inspection.after_images.map((imagePath, index) => (
                    <Image
                      key={index}
                      source={{ uri: getImageUrl(imagePath) }}
                      style={styles.image}
                      contentFit="cover"
                    />
                  ))}
                </ScrollView>
              </ThemedView>
            )}
          </ThemedView>
        )}
      </ScrollView>
    </ThemedView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
  },
  scrollView: {
    flex: 1,
  },
  scrollContent: {
    paddingBottom: 40,
  },
  header: {
    padding: 20,
    paddingTop: 60,
  },
  title: {
    fontSize: 28,
    fontWeight: 'bold',
    marginBottom: 4,
  },
  subtitle: {
    fontSize: 16,
    opacity: 0.7,
    marginBottom: 4,
  },
  date: {
    fontSize: 14,
    opacity: 0.5,
  },
  card: {
    borderRadius: 16,
    padding: 20,
    marginHorizontal: 20,
    marginBottom: 16,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 8,
    elevation: 3,
  },
  cardLabel: {
    fontSize: 14,
    opacity: 0.6,
    marginBottom: 8,
  },
  cardTitle: {
    fontSize: 18,
    fontWeight: '600',
    marginBottom: 12,
  },
  totalCost: {
    fontSize: 32,
    fontWeight: 'bold',
  },
  summaryText: {
    fontSize: 16,
    lineHeight: 24,
  },
  section: {
    paddingHorizontal: 20,
    marginBottom: 24,
  },
  sectionTitle: {
    fontSize: 20,
    fontWeight: '600',
    marginBottom: 16,
  },
  damageCard: {
    borderRadius: 12,
    padding: 16,
    marginBottom: 12,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.05,
    shadowRadius: 4,
    elevation: 2,
  },
  damageHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 8,
  },
  damagePart: {
    fontSize: 16,
    fontWeight: '600',
    flex: 1,
  },
  severityBadge: {
    paddingHorizontal: 8,
    paddingVertical: 4,
    borderRadius: 6,
  },
  severityText: {
    fontSize: 10,
    fontWeight: '700',
  },
  damageType: {
    fontSize: 14,
    opacity: 0.7,
    marginBottom: 8,
  },
  damageDescription: {
    fontSize: 14,
    lineHeight: 20,
    marginBottom: 12,
  },
  damageFooter: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingTop: 12,
    borderTopWidth: 1,
    borderTopColor: 'rgba(0,0,0,0.1)',
  },
  damageAction: {
    fontSize: 14,
    opacity: 0.7,
  },
  damageCost: {
    fontSize: 16,
    fontWeight: '600',
  },
  imageSection: {
    marginBottom: 24,
  },
  imageSectionTitle: {
    fontSize: 16,
    fontWeight: '600',
    marginBottom: 12,
  },
  image: {
    width: 200,
    height: 200,
    borderRadius: 12,
    marginRight: 12,
  },
  loadingText: {
    marginTop: 12,
    opacity: 0.6,
  },
});

