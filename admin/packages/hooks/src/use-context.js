import { inject, provide } from 'vue';
/**
 * Use context
 *
 * @example
 *   ```ts
 *   // there are three vue files: A.vue, B.vue, C.vue, and A.vue is the parent component of B.vue and C.vue
 *
 *   // context.ts
 *   import { ref } from 'vue';
 *   import { useContext } from '@sa/hooks';
 *
 *   export const { setupStore, useStore } = useContext('demo', () => {
 *     const count = ref(0);
 *
 *     function increment() {
 *       count.value++;
 *     }
 *
 *     function decrement() {
 *       count.value--;
 *     }
 *
 *     return {
 *       count,
 *       increment,
 *       decrement
 *     };
 *   })
 *   ``` // A.vue
 *   ```vue
 *   <template>
 *     <div>A</div>
 *   </template>
 *   <script setup lang="ts">
 *   import { setupStore } from './context';
 *
 *   setupStore();
 *   // const { increment } = setupStore(); // also can control the store in the parent component
 *   </script>
 *   ``` // B.vue
 *   ```vue
 *   <template>
 *    <div>B</div>
 *   </template>
 *   <script setup lang="ts">
 *   import { useStore } from './context';
 *
 *   const { count, increment } = useStore();
 *   </script>
 *   ```;
 *
 *   // C.vue is same as B.vue
 *
 * @param contextName Context name
 * @param fn Context function
 */
export default function useContext(contextName, fn) {
    const { useProvide, useInject: useStore } = createContext(contextName);
    function setupStore(...args) {
        const context = fn(...args);
        return useProvide(context);
    }
    return {
        /** Setup store in the parent component */
        setupStore,
        /** Use store in the child component */
        useStore
    };
}
/** Create context */
function createContext(contextName) {
    const injectKey = Symbol(contextName);
    function useProvide(context) {
        provide(injectKey, context);
        return context;
    }
    function useInject() {
        return inject(injectKey);
    }
    return {
        useProvide,
        useInject
    };
}
