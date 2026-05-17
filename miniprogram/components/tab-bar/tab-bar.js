Component({
  properties: {
    active: {
      type: String,
      value: "home"
    }
  },

  methods: {
    onChange(event) {
      this.triggerEvent("change", {
        tab: event.currentTarget.dataset.tab
      });
    }
  }
});
