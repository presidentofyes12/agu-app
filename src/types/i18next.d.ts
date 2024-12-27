// First, let's create a proper type for our translations
// Create a new file: src/types/i18next.d.ts
import 'react-i18next';

declare module 'react-i18next' {
  interface Resources {
    translation: {
      // Define your translation keys here
      'Sign in to get started': string;
      'Create Nostr Account': string;
      'Import Nostr Account': string;
      'Skip': string;
      'Create Account': string;
      // Add other translation keys as needed
    };
  }
}
