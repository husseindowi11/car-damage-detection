import React, { useEffect, useState } from 'react';
import {
  StyleSheet,
  ScrollView,
  ActivityIndicator,
  Alert,
  View,
  Platform,
  TouchableOpacity,
  Modal,
  Dimensions,
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
  const [activeImageTab, setActiveImageTab] = useState<'before' | 'after' | 'bounded'>('before');
  const [previewImage, setPreviewImage] = useState<string | null>(null);

  useEffect(() => {
    if (id) {
      loadInspectionDetails();
    }
  }, [id]);

  // Set default tab based on available images
  useEffect(() => {
    if (inspection) {
      if (inspection.before_images.length > 0) {
        setActiveImageTab('before');
      } else if (inspection.after_images.length > 0) {
        setActiveImageTab('after');
      } else if (inspection.bounded_images && inspection.bounded_images.length > 0) {
        setActiveImageTab('bounded');
      }
    }
  }, [inspection]);

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
      {/* Image Preview Modal */}
      <Modal
        visible={previewImage !== null}
        transparent={true}
        animationType="fade"
        onRequestClose={() => setPreviewImage(null)}
      >
        <View style={styles.modalContainer}>
          <TouchableOpacity
            style={styles.modalOverlay}
            activeOpacity={1}
            onPress={() => setPreviewImage(null)}
          >
            <View style={styles.modalContent}>
              {previewImage && (
                <Image
                  source={{ uri: previewImage }}
                  style={styles.previewImage}
                  contentFit="contain"
                />
              )}
              <TouchableOpacity
                style={styles.closeButton}
                onPress={() => setPreviewImage(null)}
              >
                <ThemedText style={styles.closeButtonText}>✕</ThemedText>
              </TouchableOpacity>
            </View>
          </TouchableOpacity>
        </View>
      </Modal>

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
        {(inspection.before_images.length > 0 || inspection.after_images.length > 0 || (inspection.bounded_images && inspection.bounded_images.length > 0)) && (
          <ThemedView style={styles.section}>
            <ThemedText style={styles.sectionTitle}>Images</ThemedText>
            
            {/* Image Tabs */}
            <ThemedView style={styles.tabContainer}>
              <TouchableOpacity
                style={[
                  styles.tab,
                  activeImageTab === 'before' && [
                    styles.tabActive,
                    { backgroundColor: colors.tint + '20', borderBottomColor: colors.tint },
                  ],
                ]}
                onPress={() => setActiveImageTab('before')}
                disabled={inspection.before_images.length === 0}
              >
                <ThemedText
                  style={[
                    styles.tabText,
                    activeImageTab === 'before' && { color: colors.tint, fontWeight: '600' },
                    inspection.before_images.length === 0 && { opacity: 0.4 },
                  ]}
                >
                  Before ({inspection.before_images.length})
                </ThemedText>
              </TouchableOpacity>

              <TouchableOpacity
                style={[
                  styles.tab,
                  activeImageTab === 'after' && [
                    styles.tabActive,
                    { backgroundColor: colors.tint + '20', borderBottomColor: colors.tint },
                  ],
                ]}
                onPress={() => setActiveImageTab('after')}
                disabled={inspection.after_images.length === 0}
              >
                <ThemedText
                  style={[
                    styles.tabText,
                    activeImageTab === 'after' && { color: colors.tint, fontWeight: '600' },
                    inspection.after_images.length === 0 && { opacity: 0.4 },
                  ]}
                >
                  After ({inspection.after_images.length})
                </ThemedText>
              </TouchableOpacity>

              {/* Bounded Images Tab (only show if damages exist) */}
              {inspection.bounded_images && inspection.bounded_images.length > 0 && (
                <TouchableOpacity
                  style={[
                    styles.tab,
                    activeImageTab === 'bounded' && [
                      styles.tabActive,
                      { backgroundColor: colors.tint + '20', borderBottomColor: colors.tint },
                    ],
                  ]}
                  onPress={() => setActiveImageTab('bounded')}
                >
                  <ThemedText
                    style={[
                      styles.tabText,
                      activeImageTab === 'bounded' && { color: colors.tint, fontWeight: '600' },
                    ]}
                  >
                    Damages ({inspection.bounded_images.length})
                  </ThemedText>
                </TouchableOpacity>
              )}
            </ThemedView>

            {/* Image Content */}
            <ThemedView style={styles.imageContent}>
              {activeImageTab === 'bounded' && inspection.bounded_images && inspection.bounded_images.length > 0 && (
                <ScrollView horizontal showsHorizontalScrollIndicator={false}>
                  {inspection.bounded_images.map((imagePath, index) => (
                    <TouchableOpacity
                      key={index}
                      onPress={() => setPreviewImage(getImageUrl(imagePath))}
                      activeOpacity={0.8}
                    >
                      <Image
                        source={{ uri: getImageUrl(imagePath) }}
                        style={styles.image}
                        contentFit="cover"
                      />
                    </TouchableOpacity>
                  ))}
                </ScrollView>
              )}

              {activeImageTab === 'before' && inspection.before_images.length > 0 && (
                <ScrollView horizontal showsHorizontalScrollIndicator={false}>
                  {inspection.before_images.map((imagePath, index) => (
                    <TouchableOpacity
                      key={index}
                      onPress={() => setPreviewImage(getImageUrl(imagePath))}
                      activeOpacity={0.8}
                    >
                      <Image
                        source={{ uri: getImageUrl(imagePath) }}
                        style={styles.image}
                        contentFit="cover"
                      />
                    </TouchableOpacity>
                  ))}
                </ScrollView>
              )}

              {activeImageTab === 'after' && inspection.after_images.length > 0 && (
                <ScrollView horizontal showsHorizontalScrollIndicator={false}>
                  {inspection.after_images.map((imagePath, index) => (
                    <TouchableOpacity
                      key={index}
                      onPress={() => setPreviewImage(getImageUrl(imagePath))}
                      activeOpacity={0.8}
                    >
                      <Image
                        source={{ uri: getImageUrl(imagePath) }}
                        style={styles.image}
                        contentFit="cover"
                      />
                    </TouchableOpacity>
                  ))}
                </ScrollView>
              )}

              {((activeImageTab === 'before' && inspection.before_images.length === 0) ||
                (activeImageTab === 'after' && inspection.after_images.length === 0) ||
                (activeImageTab === 'bounded' && (!inspection.bounded_images || inspection.bounded_images.length === 0))) && (
                <ThemedView style={styles.emptyImages}>
                  <ThemedText style={styles.emptyImagesIcon}>📷</ThemedText>
                  <ThemedText style={styles.emptyImagesTitle}>
                    No {activeImageTab === 'before' ? 'Before' : activeImageTab === 'after' ? 'After' : 'Damage'} Images
                  </ThemedText>
                  <ThemedText style={styles.emptyImagesSubtitle}>
                    {activeImageTab === 'before' 
                      ? 'No pickup images were uploaded for this inspection.'
                      : activeImageTab === 'after'
                      ? 'No return images were uploaded for this inspection.'
                      : 'No damage highlights available for this inspection.'}
                  </ThemedText>
                </ThemedView>
              )}
            </ThemedView>
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
    // iOS shadow
    ...(Platform.OS === 'ios' && {
      shadowColor: '#000',
      shadowOffset: { width: 0, height: 2 },
      shadowOpacity: 0.1,
      shadowRadius: 8,
    }),
    // Android elevation
    ...(Platform.OS === 'android' && {
      elevation: 3,
    }),
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
    lineHeight: 40,
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
    // iOS shadow
    ...(Platform.OS === 'ios' && {
      shadowColor: '#000',
      shadowOffset: { width: 0, height: 1 },
      shadowOpacity: 0.05,
      shadowRadius: 4,
    }),
    // Android elevation
    ...(Platform.OS === 'android' && {
      elevation: 2,
    }),
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
  tabContainer: {
    flexDirection: 'row',
    marginBottom: 16,
    backgroundColor: 'transparent',
    borderRadius: 12,
    overflow: 'hidden',
  },
  tab: {
    flex: 1,
    paddingVertical: 12,
    paddingHorizontal: 16,
    alignItems: 'center',
    justifyContent: 'center',
    borderBottomWidth: 2,
    borderBottomColor: 'transparent',
  },
  tabActive: {
    borderBottomWidth: 2,
  },
  tabText: {
    fontSize: 13,
    fontWeight: '500',
  },
  imageContent: {
    minHeight: 220,
  },
  image: {
    width: 200,
    height: 200,
    borderRadius: 12,
    marginRight: 12,
  },
  emptyImages: {
    padding: 40,
    alignItems: 'center',
    justifyContent: 'center',
  },
  emptyImagesIcon: {
    fontSize: 48,
    marginBottom: 12,
    opacity: 0.3,
  },
  emptyImagesTitle: {
    fontSize: 18,
    fontWeight: '600',
    marginBottom: 8,
    textAlign: 'center',
  },
  emptyImagesSubtitle: {
    fontSize: 14,
    opacity: 0.6,
    textAlign: 'center',
    paddingHorizontal: 20,
  },
  loadingText: {
    marginTop: 12,
    opacity: 0.6,
  },
  modalContainer: {
    flex: 1,
    backgroundColor: 'rgba(0, 0, 0, 0.95)',
  },
  modalOverlay: {
    flex: 1,
  },
  modalContent: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
  },
  previewImage: {
    width: Dimensions.get('window').width,
    height: Dimensions.get('window').height,
  },
  closeButton: {
    position: 'absolute',
    top: Platform.OS === 'ios' ? 60 : 40,
    right: 20,
    width: 44,
    height: 44,
    borderRadius: 22,
    backgroundColor: 'rgba(255, 255, 255, 0.3)',
    justifyContent: 'center',
    alignItems: 'center',
    zIndex: 10,
  },
  closeButtonText: {
    fontSize: 24,
    color: '#fff',
    fontWeight: 'bold',
  },
});

