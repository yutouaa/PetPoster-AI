Component({
  properties: {
    title: {
      type: String,
      value: ""
    },
    showBack: {
      type: Boolean,
      value: false
    },
    rightCapsule: {
      type: Boolean,
      value: true
    }
  },

  methods: {
    onBack() {
      this.triggerEvent("back");
    }
  }
});
