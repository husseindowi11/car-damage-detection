import { Redirect } from 'expo-router';

/**
 * Index route for tabs - redirects to inspections as the default tab
 * This is required for iOS routing to work properly
 */
export default function Index() {
  return <Redirect href="/(tabs)/inspections" />;
}

