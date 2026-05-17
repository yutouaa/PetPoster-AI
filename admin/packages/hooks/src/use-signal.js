import { computed, ref, shallowRef, triggerRef } from 'vue';
export function useSignal(initialValue, options) {
    const { useRef } = options || {};
    const state = useRef ? ref(initialValue) : shallowRef(initialValue);
    return createSignal(state);
}
export function useComputed(getterOrOptions, debugOptions) {
    const isGetter = typeof getterOrOptions === 'function';
    const computedValue = computed(getterOrOptions, debugOptions);
    if (isGetter) {
        return () => computedValue.value;
    }
    return createSignal(computedValue);
}
function createSignal(state) {
    const signal = () => state.value;
    signal.set = (value) => {
        state.value = value;
    };
    signal.update = (updater) => {
        state.value = updater(state.value);
    };
    signal.mutate = (mutator) => {
        mutator(state.value);
        triggerRef(state);
    };
    signal.getRef = () => state;
    return signal;
}
