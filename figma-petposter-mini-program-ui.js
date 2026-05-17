/**
 * PetPoster AI Mini Program Figma generator.
 *
 * Usage: run this as the main code of a temporary Figma plugin while a design
 * file is open. It creates a fresh page named "PetPoster AI Mini Program" with
 * 6 high-fidelity WeChat mini-program screens, local styles, component samples,
 * and prototype links.
 */

const PAGE_NAME = "PetPoster AI Mini Program";
const TOKEN_COLLECTION_NAME = "PetPoster AI Tokens";

const COLORS = {
  primary: "#2d2520",
  primarySoft: "#5d514a",
  primaryMuted: "#8b7a70",
  brand: "#d97757",
  brandLight: "#e89b7d",
  brandTint: "#fff1e8",
  bgWarm: "#fdfbf7",
  bgCool: "#f5f1ec",
  surface: "#ffffff",
  surfaceCream: "#fffaf3",
  border: "#eadfd5",
  borderStrong: "#dccbbd",
  teal: "#52a67d",
  tealLight: "#dff4ea",
  blue: "#6f8edb",
  blueLight: "#e8eefc",
  lavender: "#b89ae9",
  lavenderLight: "#f1eafd",
  warning: "#e8a05d",
  warningLight: "#fff2dd",
  success: "#52a67d",
  ink: "#111827",
  gray600: "#4b5563",
  gray400: "#9ca3af",
  gray100: "#f3f4f6",
  gray50: "#f9fafb"
};

const SPACE = {
  s2: 8,
  s3: 12,
  s4: 16,
  s5: 20,
  s6: 24,
  s8: 32
};

const SCREEN = {
  width: 390,
  height: 844,
  nav: 94,
  tabbar: 82,
  bottomBar: 96
};

const RADIUS = {
  sm: 8,
  md: 12,
  lg: 16,
  xl: 20,
  xxl: 28,
  pill: 999
};

const created = {
  pages: [],
  frames: [],
  components: [],
  styles: [],
  variables: [],
  prototypeNodes: []
};

function hexToRgb(hex) {
  const normalized = hex.replace("#", "");
  const bigint = parseInt(normalized, 16);
  return {
    r: ((bigint >> 16) & 255) / 255,
    g: ((bigint >> 8) & 255) / 255,
    b: (bigint & 255) / 255
  };
}

function solid(hex, opacity = 1) {
  return {
    type: "SOLID",
    color: hexToRgb(hex),
    opacity
  };
}

function gradient(from, to, accent) {
  const stops = [
    { position: 0, color: { ...hexToRgb(from), a: 1 } },
    { position: 1, color: { ...hexToRgb(to), a: 1 } }
  ];
  if (accent) {
    stops.splice(1, 0, { position: 0.48, color: { ...hexToRgb(accent), a: 1 } });
  }
  return {
    type: "GRADIENT_LINEAR",
    gradientTransform: [
      [0.74, 0.68, -0.18],
      [-0.68, 0.74, 0.47]
    ],
    gradientStops: stops
  };
}

function shadow(level = "sm") {
  const map = {
    xs: { radius: 8, offset: 2, opacity: 0.05 },
    sm: { radius: 14, offset: 4, opacity: 0.08 },
    md: { radius: 22, offset: 8, opacity: 0.1 },
    lg: { radius: 34, offset: 14, opacity: 0.12 },
    xl: { radius: 48, offset: 20, opacity: 0.14 }
  };
  const item = map[level] || map.sm;
  return [
    {
      type: "DROP_SHADOW",
      color: { r: 0.18, g: 0.14, b: 0.11, a: item.opacity },
      offset: { x: 0, y: item.offset },
      radius: item.radius,
      spread: 0,
      visible: true,
      blendMode: "NORMAL"
    }
  ];
}

async function pickFonts() {
  const available = await figma.listAvailableFontsAsync();
  const families = [
    "PingFang SC",
    "Noto Sans SC",
    "Microsoft YaHei",
    "Source Han Sans SC",
    "Inter",
    "Arial"
  ];

  function pick(stylePrefs) {
    for (const family of families) {
      for (const style of stylePrefs) {
        const found = available.find((item) => item.fontName.family === family && item.fontName.style === style);
        if (found) return found.fontName;
      }
      const familyFallback = available.find((item) => item.fontName.family === family);
      if (familyFallback) return familyFallback.fontName;
    }
    return available[0].fontName;
  }

  const fonts = {
    regular: pick(["Regular", "Normal", "Book"]),
    medium: pick(["Medium", "Regular", "Normal"]),
    semibold: pick(["Semibold", "Semi Bold", "Demi Bold", "Medium", "Bold"]),
    bold: pick(["Bold", "Semibold", "Semi Bold", "Medium"]),
    extraBold: pick(["ExtraBold", "Extra Bold", "Black", "Bold"])
  };

  const unique = new Map(Object.values(fonts).map((font) => [`${font.family}/${font.style}`, font]));
  await Promise.all([...unique.values()].map((font) => figma.loadFontAsync(font)));
  return fonts;
}

function setAbsolute(node, x, y, width, height) {
  node.x = x;
  node.y = y;
  if (typeof width === "number" && typeof height === "number") {
    node.resize(width, height);
  }
}

function frame(parent, name, x, y, width, height, options = {}) {
  const node = figma.createFrame();
  node.name = name;
  node.clipsContent = options.clipsContent ?? false;
  node.fills = options.fills || [solid(options.fill || COLORS.surface)];
  node.strokes = options.stroke ? [solid(options.stroke)] : [];
  node.strokeWeight = options.stroke ? options.strokeWeight || 1 : 0;
  node.cornerRadius = options.radius ?? 0;
  if (options.effects) node.effects = options.effects;
  parent.appendChild(node);
  setAbsolute(node, x, y, width, height);
  return node;
}

function rect(parent, name, x, y, width, height, options = {}) {
  const node = figma.createRectangle();
  node.name = name;
  node.fills = options.fills || [solid(options.fill || COLORS.surface, options.opacity ?? 1)];
  node.strokes = options.stroke ? [solid(options.stroke, options.strokeOpacity ?? 1)] : [];
  node.strokeWeight = options.stroke ? options.strokeWeight || 1 : 0;
  node.cornerRadius = options.radius ?? 0;
  if (options.effects) node.effects = options.effects;
  if (typeof options.opacity === "number") node.opacity = options.opacity;
  parent.appendChild(node);
  setAbsolute(node, x, y, width, height);
  return node;
}

function ellipse(parent, name, x, y, width, height, options = {}) {
  const node = figma.createEllipse();
  node.name = name;
  node.fills = options.fills || [solid(options.fill || COLORS.surface, options.opacity ?? 1)];
  node.strokes = options.stroke ? [solid(options.stroke)] : [];
  node.strokeWeight = options.stroke ? options.strokeWeight || 1 : 0;
  if (options.effects) node.effects = options.effects;
  if (typeof options.opacity === "number") node.opacity = options.opacity;
  parent.appendChild(node);
  setAbsolute(node, x, y, width, height);
  return node;
}

function text(parent, name, characters, x, y, width, options = {}) {
  const node = figma.createText();
  node.name = name;
  node.fontName = options.font || FONTS.regular;
  node.characters = characters;
  node.fontSize = options.size || 14;
  node.lineHeight = { unit: "PIXELS", value: options.lineHeight || Math.round((options.size || 14) * 1.35) };
  node.letterSpacing = { unit: "PIXELS", value: 0 };
  node.fills = [solid(options.color || COLORS.primary)];
  node.textAutoResize = width ? "HEIGHT" : "WIDTH_AND_HEIGHT";
  if (width) node.resize(width, node.height);
  parent.appendChild(node);
  node.x = x;
  node.y = y;
  return node;
}

function addAmbientWashes(screen) {
  rect(screen, "ambient wash / top", 0, 0, SCREEN.width, 220, {
    fills: [gradient("#fffaf3", "#f4e3d8", "#f8efe7")],
    opacity: 0.42
  });
  rect(screen, "ambient wash / bottom", 0, 560, SCREEN.width, 180, {
    fills: [gradient("#f6f1ec", "#e8eefc", "#fdfbf7")],
    opacity: 0.26
  });
}

function addStatusBar(screen) {
  text(screen, "status / time", "9:41", 24, 16, 80, { size: 14, font: FONTS.semibold, color: COLORS.primary });
  const right = frame(screen, "status / right icons", 300, 17, 68, 14, { fill: "#ffffff", clipsContent: false });
  right.fills = [];
  rect(right, "cell", 0, 5, 18, 8, { fill: COLORS.primary, radius: 2, opacity: 0.85 });
  rect(right, "wifi", 27, 4, 16, 9, { fill: COLORS.primary, radius: 4, opacity: 0.85 });
  rect(right, "battery", 50, 3, 17, 10, { fill: COLORS.primary, radius: 3, opacity: 0.85 });
}

function addNav(screen, kicker, title, back = false) {
  addStatusBar(screen);
  if (back) {
    const btn = frame(screen, "nav / back button", 20, 51, 38, 38, {
      fill: COLORS.surface,
      radius: RADIUS.pill,
      effects: shadow("xs")
    });
    rect(btn, "chevron left / stem", 15, 11, 3, 16, { fill: COLORS.primary, radius: 2 });
    rect(btn, "chevron left / arm", 15, 11, 14, 3, { fill: COLORS.primary, radius: 2 });
    btn.rotation = 45;
    text(screen, "nav / kicker", kicker, 68, 50, 180, {
      size: 11,
      lineHeight: 14,
      font: FONTS.semibold,
      color: COLORS.primaryMuted
    });
    text(screen, "nav / title", title, 68, 68, 220, {
      size: 22,
      lineHeight: 28,
      font: FONTS.bold,
      color: COLORS.primary
    });
    return btn;
  }
  text(screen, "nav / kicker", kicker, 24, 50, 210, {
    size: 11,
    lineHeight: 14,
    font: FONTS.semibold,
    color: COLORS.primaryMuted
  });
  text(screen, "nav / title", title, 24, 68, 240, {
    size: 24,
    lineHeight: 30,
    font: FONTS.bold,
    color: COLORS.primary
  });
  return null;
}

function plusIcon(parent, x, y, color = COLORS.brand) {
  const wrap = frame(parent, "icon / plus", x, y, 26, 26, { fill: "#ffffff" });
  wrap.fills = [];
  rect(wrap, "plus vertical", 12, 5, 3, 16, { fill: color, radius: 2 });
  rect(wrap, "plus horizontal", 5, 12, 16, 3, { fill: color, radius: 2 });
  return wrap;
}

function arrowIcon(parent, x, y, color = COLORS.surface) {
  const wrap = frame(parent, "icon / arrow", x, y, 24, 18, { fill: "#ffffff" });
  wrap.fills = [];
  rect(wrap, "arrow shaft", 3, 8, 15, 2.8, { fill: color, radius: 2 });
  rect(wrap, "arrow head top", 14, 4, 9, 2.8, { fill: color, radius: 2 });
  rect(wrap, "arrow head bottom", 14, 12, 9, 2.8, { fill: color, radius: 2 });
  wrap.children[1].rotation = 38;
  wrap.children[2].rotation = -38;
  return wrap;
}

function checkIcon(parent, x, y) {
  const wrap = frame(parent, "icon / check", x, y, 26, 26, {
    fill: COLORS.brand,
    radius: RADIUS.pill
  });
  rect(wrap, "check short", 7, 13, 7, 3, { fill: COLORS.surface, radius: 2 });
  rect(wrap, "check long", 12, 10, 12, 3, { fill: COLORS.surface, radius: 2 });
  wrap.children[0].rotation = 42;
  wrap.children[1].rotation = -42;
  return wrap;
}

function petFace(parent, x, y, scale = 1, options = {}) {
  const group = frame(parent, "pet visual", x, y, 92 * scale, 82 * scale, { fill: "#ffffff" });
  group.fills = [];
  ellipse(group, "left ear", 8 * scale, 2 * scale, 30 * scale, 38 * scale, {
    fill: options.ear || COLORS.brandLight,
    opacity: 0.92
  });
  ellipse(group, "right ear", 54 * scale, 2 * scale, 30 * scale, 38 * scale, {
    fill: options.ear || COLORS.brandLight,
    opacity: 0.92
  });
  ellipse(group, "face", 18 * scale, 16 * scale, 56 * scale, 56 * scale, {
    fill: options.face || COLORS.surface,
    effects: shadow("xs")
  });
  ellipse(group, "left eye", 34 * scale, 38 * scale, 6 * scale, 7 * scale, { fill: COLORS.primary });
  ellipse(group, "right eye", 54 * scale, 38 * scale, 6 * scale, 7 * scale, { fill: COLORS.primary });
  ellipse(group, "nose", 44 * scale, 49 * scale, 9 * scale, 7 * scale, { fill: COLORS.brand });
  rect(group, "muzzle", 38 * scale, 56 * scale, 20 * scale, 5 * scale, {
    fill: options.muzzle || COLORS.border,
    radius: RADIUS.pill,
    opacity: 0.75
  });
  return group;
}

function pawMark(parent, x, y, size = 24, color = COLORS.brand) {
  const group = frame(parent, "paw mark", x, y, size, size, { fill: "#ffffff" });
  group.fills = [];
  ellipse(group, "pad", size * 0.32, size * 0.42, size * 0.36, size * 0.32, { fill: color, opacity: 0.9 });
  ellipse(group, "toe 1", size * 0.18, size * 0.22, size * 0.18, size * 0.2, { fill: color, opacity: 0.9 });
  ellipse(group, "toe 2", size * 0.42, size * 0.12, size * 0.18, size * 0.2, { fill: color, opacity: 0.9 });
  ellipse(group, "toe 3", size * 0.65, size * 0.22, size * 0.18, size * 0.2, { fill: color, opacity: 0.9 });
  return group;
}

function primaryButton(parent, name, label, x, y, width, options = {}) {
  const btn = frame(parent, name, x, y, width, options.height || 56, {
    fills: [gradient(COLORS.brand, COLORS.brandLight)],
    radius: RADIUS.lg,
    effects: shadow("md")
  });
  text(btn, "label", label, 22, 17, width - 70, {
    size: 16,
    lineHeight: 22,
    font: FONTS.semibold,
    color: COLORS.surface
  });
  arrowIcon(btn, width - 46, 19, COLORS.surface);
  return btn;
}

function secondaryButton(parent, name, label, x, y, width, options = {}) {
  const btn = frame(parent, name, x, y, width, options.height || 52, {
    fill: options.fill || COLORS.surface,
    radius: RADIUS.md,
    stroke: options.stroke || COLORS.border,
    effects: options.effects || []
  });
  text(btn, "label", label, 0, 16, width, {
    size: 14,
    lineHeight: 20,
    font: FONTS.semibold,
    color: options.color || COLORS.primary
  }).textAlignHorizontal = "CENTER";
  return btn;
}

function categoryPill(parent, label, x, y, active = false, width = 72) {
  const pill = frame(parent, `category / ${label}`, x, y, width, 36, {
    fill: active ? COLORS.primary : COLORS.surface,
    radius: RADIUS.pill,
    stroke: active ? COLORS.primary : COLORS.border
  });
  text(pill, "label", label, 0, 9, width, {
    size: 13,
    lineHeight: 18,
    font: FONTS.semibold,
    color: active ? COLORS.surface : COLORS.primarySoft
  }).textAlignHorizontal = "CENTER";
  return pill;
}

function tabbar(parent, active = "home") {
  const bar = frame(parent, "tabbar", 0, SCREEN.height - SCREEN.tabbar, SCREEN.width, SCREEN.tabbar, {
    fill: COLORS.surface,
    stroke: COLORS.border,
    radius: 0,
    effects: shadow("xs")
  });
  const home = frame(bar, "tab / home", 74, 12, 92, 58, { fill: "#ffffff" });
  const mine = frame(bar, "tab / mine", 224, 12, 92, 58, { fill: "#ffffff" });
  home.fills = [];
  mine.fills = [];
  const homeActive = active === "home";
  const mineActive = active === "mine";

  rect(home, "home roof", 34, 8, 24, 18, { fill: homeActive ? COLORS.brand : COLORS.primaryMuted, radius: 4 });
  rect(home, "home base", 39, 22, 14, 13, { fill: homeActive ? COLORS.brand : COLORS.primaryMuted, radius: 3 });
  text(home, "label", "首页", 0, 39, 92, {
    size: 12,
    lineHeight: 16,
    font: FONTS.semibold,
    color: homeActive ? COLORS.brand : COLORS.primaryMuted
  }).textAlignHorizontal = "CENTER";

  ellipse(mine, "head", 39, 8, 14, 14, { fill: mineActive ? COLORS.brand : COLORS.primaryMuted });
  rect(mine, "body", 33, 24, 26, 12, { fill: mineActive ? COLORS.brand : COLORS.primaryMuted, radius: RADIUS.pill });
  text(mine, "label", "我的", 0, 39, 92, {
    size: 12,
    lineHeight: 16,
    font: FONTS.semibold,
    color: mineActive ? COLORS.brand : COLORS.primaryMuted
  }).textAlignHorizontal = "CENTER";
  return { bar, home, mine };
}

function screenShell(name, x, y, navKicker, navTitle, options = {}) {
  const screen = frame(figma.currentPage, `Screen / ${name}`, x, y, SCREEN.width, SCREEN.height, {
    fills: [gradient(COLORS.bgWarm, COLORS.bgCool, "#fff6ee")],
    radius: 0,
    clipsContent: true
  });
  created.frames.push(screen.id);
  addAmbientWashes(screen);
  const back = addNav(screen, navKicker, navTitle, options.back);
  return { screen, back };
}

function drawPhotoSlot(parent, index, x, y, state = "photo") {
  const fills = [
    gradient("#fff6eb", "#ead7c5"),
    gradient("#e8eefc", "#d9e4ff"),
    gradient("#edf6ee", "#d8efe3"),
    gradient("#fff2dd", "#ecd6bb")
  ];
  const slot = frame(parent, `photo slot / ${index}`, x, y, 98, 98, {
    fills: state === "add" ? [solid(COLORS.brandTint)] : [fills[index % fills.length]],
    radius: RADIUS.lg,
    stroke: state === "add" ? COLORS.brandLight : COLORS.surface,
    strokeWeight: state === "add" ? 1.5 : 0,
    clipsContent: true,
    effects: state === "empty" ? [] : shadow("xs")
  });
  if (state === "add") {
    plusIcon(slot, 36, 26, COLORS.brand);
    text(slot, "add label", "继续添加", 0, 60, 98, {
      size: 12,
      lineHeight: 16,
      font: FONTS.semibold,
      color: COLORS.brand
    }).textAlignHorizontal = "CENTER";
    return slot;
  }
  if (state === "empty") {
    slot.fills = [solid("#ffffff", 0.42)];
    slot.strokes = [solid(COLORS.border, 0.8)];
    slot.dashPattern = [6, 6];
    return slot;
  }
  petFace(slot, 12, 10, 0.78, {
    ear: index % 2 === 0 ? COLORS.brandLight : COLORS.blue,
    face: COLORS.surfaceCream
  });
  if (index === 0) {
    pawMark(slot, 70, 68, 20, COLORS.brand);
  }
  const del = frame(slot, "delete", 70, 8, 20, 20, { fill: COLORS.surface, radius: RADIUS.pill });
  rect(del, "delete x 1", 6, 9, 8, 2, { fill: COLORS.primaryMuted, radius: 2 });
  rect(del, "delete x 2", 6, 9, 8, 2, { fill: COLORS.primaryMuted, radius: 2 });
  del.children[0].rotation = 45;
  del.children[1].rotation = -45;
  return slot;
}

function drawPosterCard(parent, name, x, y, width, height, config = {}) {
  const card = frame(parent, name, x, y, width, height, {
    fills: [config.gradient || gradient("#3a302b", "#b67355", COLORS.brandLight)],
    radius: config.radius || RADIUS.xl,
    clipsContent: true,
    stroke: config.selected ? COLORS.brand : undefined,
    strokeWeight: config.selected ? 2 : 0,
    effects: shadow(config.large ? "lg" : "sm")
  });
  const ribbon = rect(card, "poster accent ribbon", width - 86, -26, 78, height + 72, {
    fill: config.accent || COLORS.teal,
    radius: RADIUS.xl,
    opacity: 0.18
  });
  ribbon.rotation = 13;
  const stripe = rect(card, "poster paper stripe", 18, 26, Math.max(72, width * 0.42), 10, {
    fill: config.dot || COLORS.blue,
    radius: RADIUS.pill,
    opacity: 0.2
  });
  stripe.rotation = -3;
  petFace(card, width / 2 - 48, height / 2 - 54, config.large ? 1.05 : 0.86, {
    ear: config.ear || COLORS.brandLight,
    face: COLORS.surface
  });
  rect(card, "bottom scrim", 0, height - 82, width, 82, {
    fills: [solid(COLORS.primary, 0.55)]
  });
  card.children[card.children.length - 1].fills = [
    {
      type: "GRADIENT_LINEAR",
      gradientTransform: [
        [0, 1, 0],
        [-1, 0, 1]
      ],
      gradientStops: [
        { position: 0, color: { r: 0.18, g: 0.14, b: 0.11, a: 0 } },
        { position: 1, color: { r: 0.18, g: 0.14, b: 0.11, a: 0.68 } }
      ]
    }
  ];
  text(card, "style name", config.title || "城市杂志封面", 16, height - 62, width - 70, {
    size: config.large ? 18 : 14,
    lineHeight: config.large ? 24 : 19,
    font: FONTS.bold,
    color: COLORS.surface
  });
  text(card, "style desc", config.desc || "后台图片 · 推荐展示位", 16, height - 34, width - 56, {
    size: 12,
    lineHeight: 16,
    font: FONTS.medium,
    color: "#fff1e8"
  });
  if (config.selected) checkIcon(card, width - 42, height - 52);
  return card;
}

function addScreenLabel(title, x, y) {
  text(figma.currentPage, `label / ${title}`, title, x, y, 390, {
    size: 18,
    lineHeight: 24,
    font: FONTS.bold,
    color: COLORS.primary
  });
}

async function ensureStyles() {
  const paintStyles = await figma.getLocalPaintStylesAsync();
  const textStyles = await figma.getLocalTextStylesAsync();
  const effectStyles = await figma.getLocalEffectStylesAsync();

  function paintStyle(name, paint) {
    const full = `PetPoster/${name}`;
    const existing = paintStyles.find((style) => style.name === full);
    const style = existing || figma.createPaintStyle();
    style.name = full;
    style.paints = [paint];
    if (!existing) created.styles.push(style.id);
    return style;
  }

  function typographyStyle(name, font, size, lineHeight, color = COLORS.primary) {
    const full = `PetPoster/${name}`;
    const existing = textStyles.find((style) => style.name === full);
    const style = existing || figma.createTextStyle();
    style.name = full;
    style.fontName = font;
    style.fontSize = size;
    style.lineHeight = { unit: "PIXELS", value: lineHeight };
    style.letterSpacing = { unit: "PIXELS", value: 0 };
    style.fills = [solid(color)];
    if (!existing) created.styles.push(style.id);
    return style;
  }

  function effectStyle(name, effects) {
    const full = `PetPoster/${name}`;
    const existing = effectStyles.find((style) => style.name === full);
    const style = existing || figma.createEffectStyle();
    style.name = full;
    style.effects = effects;
    if (!existing) created.styles.push(style.id);
    return style;
  }

  paintStyle("Brand/Primary", solid(COLORS.brand));
  paintStyle("Brand/Light", solid(COLORS.brandLight));
  paintStyle("Accent/Teal", solid(COLORS.teal));
  paintStyle("Accent/Blue", solid(COLORS.blue));
  paintStyle("Surface/Base", solid(COLORS.surface));
  paintStyle("Text/Primary", solid(COLORS.primary));
  paintStyle("Border/Default", solid(COLORS.border));
  typographyStyle("Title/Large", FONTS.bold, 24, 30);
  typographyStyle("Title/Section", FONTS.bold, 20, 26);
  typographyStyle("Body/Default", FONTS.regular, 14, 20, COLORS.primarySoft);
  typographyStyle("Caption/Muted", FONTS.medium, 12, 16, COLORS.primaryMuted);
  effectStyle("Shadow/Card", shadow("sm"));
  effectStyle("Shadow/Floating", shadow("lg"));
}

async function ensureVariables() {
  if (!figma.variables) return;
  try {
    const collections = await figma.variables.getLocalVariableCollectionsAsync();
    const existing = collections.find((collection) => collection.name === TOKEN_COLLECTION_NAME);
    const collection = existing || figma.variables.createVariableCollection(TOKEN_COLLECTION_NAME);
    const modeId = collection.modes[0].modeId;
    const localVars = await figma.variables.getLocalVariablesAsync();

    function ensureVariable(name, type, value, scopes) {
      const variable =
        localVars.find((item) => item.name === name && item.variableCollectionId === collection.id) ||
        figma.variables.createVariable(name, collection, type);
      variable.scopes = scopes;
      variable.setValueForMode(modeId, value);
      created.variables.push(variable.id);
      return variable;
    }

    ensureVariable("color/brand/primary", "COLOR", { ...hexToRgb(COLORS.brand), a: 1 }, ["FRAME_FILL", "SHAPE_FILL", "TEXT_FILL"]);
    ensureVariable("color/accent/teal", "COLOR", { ...hexToRgb(COLORS.teal), a: 1 }, ["FRAME_FILL", "SHAPE_FILL", "TEXT_FILL"]);
    ensureVariable("color/accent/blue", "COLOR", { ...hexToRgb(COLORS.blue), a: 1 }, ["FRAME_FILL", "SHAPE_FILL", "TEXT_FILL"]);
    ensureVariable("color/surface/base", "COLOR", { ...hexToRgb(COLORS.surface), a: 1 }, ["FRAME_FILL", "SHAPE_FILL"]);
    ensureVariable("color/text/primary", "COLOR", { ...hexToRgb(COLORS.primary), a: 1 }, ["TEXT_FILL"]);
    ensureVariable("radius/card", "FLOAT", 16, ["CORNER_RADIUS"]);
    ensureVariable("radius/panel", "FLOAT", 20, ["CORNER_RADIUS"]);
    ensureVariable("space/page-x", "FLOAT", 24, ["GAP"]);
    ensureVariable("space/card-gap", "FLOAT", 12, ["GAP"]);
  } catch (error) {
    // Some Figma plans or plugin contexts restrict variables. Styles still cover
    // the design system deliverable if variable creation is not available.
    created.variables.push(`variables-skipped:${error.message}`);
  }
}

function makeComponent(name, width, height, builder) {
  const component = figma.createComponent();
  component.name = `Component / ${name}`;
  component.resize(width, height);
  component.fills = [solid(COLORS.surface)];
  component.cornerRadius = RADIUS.md;
  builder(component);
  figma.currentPage.appendChild(component);
  created.components.push(component.id);
  return component;
}

function createComponentLibrary(x, y) {
  text(figma.currentPage, "components heading", "PetPoster AI Components", x, y, 460, {
    size: 22,
    lineHeight: 28,
    font: FONTS.bold,
    color: COLORS.primary
  });
  text(figma.currentPage, "components caption", "可复用组件样例：导航、底栏、按钮、照片格、风格卡、海报、进度、历史、菜单。", x, y + 34, 620, {
    size: 13,
    lineHeight: 18,
    font: FONTS.regular,
    color: COLORS.primaryMuted
  });

  const nav = makeComponent("MiniProgram Nav", 240, 70, (root) => {
    root.fills = [solid(COLORS.bgWarm)];
    text(root, "kicker", "WeChat Mini Program", 0, 0, 220, {
      size: 11,
      lineHeight: 14,
      font: FONTS.semibold,
      color: COLORS.primaryMuted
    });
    text(root, "title", "宠物海报", 0, 20, 220, {
      size: 24,
      lineHeight: 30,
      font: FONTS.bold,
      color: COLORS.primary
    });
  });
  nav.x = x;
  nav.y = y + 82;

  const btn = makeComponent("Primary Button", 220, 56, (root) => {
    root.fills = [gradient(COLORS.brand, COLORS.brandLight)];
    root.cornerRadius = RADIUS.lg;
    root.effects = shadow("md");
    text(root, "label", "选择海报风格", 22, 17, 152, {
      size: 16,
      lineHeight: 22,
      font: FONTS.semibold,
      color: COLORS.surface
    });
    arrowIcon(root, 178, 19);
  });
  btn.x = x + 280;
  btn.y = y + 82;

  const tab = makeComponent("Bottom Tabbar", 310, 82, (root) => {
    root.cornerRadius = 0;
    root.strokes = [solid(COLORS.border)];
    root.strokeWeight = 1;
    const t = tabbar(root, "home");
    t.bar.x = 0;
    t.bar.y = 0;
    t.bar.resize(310, 82);
    t.home.x = 46;
    t.mine.x = 178;
  });
  tab.x = x + 540;
  tab.y = y + 72;

  const slot = makeComponent("Photo Slot", 98, 98, (root) => {
    root.fills = [gradient("#fff6eb", "#ead7c5")];
    root.cornerRadius = RADIUS.lg;
    petFace(root, 12, 10, 0.78, { ear: COLORS.brandLight, face: COLORS.surfaceCream });
    pawMark(root, 70, 68, 20, COLORS.brand);
  });
  slot.x = x;
  slot.y = y + 180;

  const styleCard = makeComponent("Poster Style Card", 160, 210, (root) => {
    root.fills = [gradient("#3a302b", "#b67355", COLORS.brandLight)];
    root.cornerRadius = RADIUS.xl;
    root.clipsContent = true;
    petFace(root, 34, 48, 0.95, { ear: COLORS.brandLight, face: COLORS.surface });
    text(root, "name", "城市杂志封面", 16, 154, 118, {
      size: 14,
      lineHeight: 19,
      font: FONTS.bold,
      color: COLORS.surface
    });
    text(root, "desc", "后台图片 · 推荐", 16, 178, 120, {
      size: 12,
      lineHeight: 16,
      font: FONTS.medium,
      color: "#fff1e8"
    });
  });
  styleCard.x = x + 134;
  styleCard.y = y + 180;

  const poster = makeComponent("Generated Poster Preview", 170, 230, (root) => {
    root.fills = [gradient("#1f2937", "#b67355", COLORS.blue)];
    root.cornerRadius = RADIUS.xl;
    root.clipsContent = true;
    text(root, "brand", "PetPoster AI", 18, 18, 134, {
      size: 13,
      lineHeight: 18,
      font: FONTS.semibold,
      color: COLORS.surface
    });
    petFace(root, 39, 66, 1, { ear: COLORS.brandLight, face: COLORS.surface });
    text(root, "title", "Natural Studio", 18, 176, 134, {
      size: 18,
      lineHeight: 24,
      font: FONTS.bold,
      color: COLORS.surface
    });
  });
  poster.x = x + 330;
  poster.y = y + 180;

  const progress = makeComponent("Progress Panel", 260, 120, (root) => {
    root.fills = [solid(COLORS.surface)];
    root.cornerRadius = RADIUS.xl;
    root.effects = shadow("sm");
    text(root, "title", "正在生成海报", 20, 18, 200, {
      size: 18,
      lineHeight: 24,
      font: FONTS.bold,
      color: COLORS.primary
    });
    rect(root, "track", 20, 66, 220, 10, { fill: COLORS.border, radius: RADIUS.pill });
    rect(root, "fill", 20, 66, 154, 10, { fill: COLORS.brand, radius: RADIUS.pill });
    text(root, "value", "72%", 204, 86, 36, {
      size: 13,
      lineHeight: 18,
      font: FONTS.semibold,
      color: COLORS.brand
    });
  });
  progress.x = x + 540;
  progress.y = y + 188;

  const historyCard = makeComponent("History Record Card", 320, 104, (root) => {
    root.fills = [solid(COLORS.surface)];
    root.cornerRadius = RADIUS.lg;
    root.effects = shadow("xs");
    drawPosterCard(root, "cover", 12, 12, 78, 80, {
      title: "",
      desc: "",
      gradient: gradient("#3a302b", "#b67355"),
      radius: RADIUS.md
    });
    text(root, "title", "城市杂志封面", 106, 20, 160, {
      size: 15,
      lineHeight: 20,
      font: FONTS.semibold,
      color: COLORS.primary
    });
    text(root, "meta", "3 张照片 · 今天 10:24", 106, 45, 160, {
      size: 12,
      lineHeight: 16,
      font: FONTS.regular,
      color: COLORS.primaryMuted
    });
    rect(root, "badge bg", 106, 68, 56, 24, { fill: COLORS.tealLight, radius: RADIUS.pill });
    text(root, "badge", "已完成", 106, 73, 56, {
      size: 11,
      lineHeight: 14,
      font: FONTS.semibold,
      color: COLORS.teal
    }).textAlignHorizontal = "CENTER";
  });
  historyCard.x = x + 840;
  historyCard.y = y + 180;

  const menuRow = makeComponent("Mine Menu Row", 320, 72, (root) => {
    root.fills = [solid(COLORS.surface)];
    root.cornerRadius = RADIUS.md;
    rect(root, "icon bg", 16, 16, 40, 40, { fill: COLORS.brandTint, radius: RADIUS.md });
    pawMark(root, 24, 23, 24, COLORS.brand);
    text(root, "title", "生成历史", 70, 16, 168, {
      size: 15,
      lineHeight: 20,
      font: FONTS.semibold,
      color: COLORS.primary
    });
    text(root, "copy", "查看并重新编辑海报", 70, 39, 168, {
      size: 12,
      lineHeight: 16,
      font: FONTS.regular,
      color: COLORS.primaryMuted
    });
    text(root, "chevron", "›", 294, 24, 12, {
      size: 20,
      lineHeight: 24,
      font: FONTS.bold,
      color: COLORS.primaryMuted
    });
  });
  menuRow.x = x + 840;
  menuRow.y = y + 304;
}

function drawHome(x, y) {
  addScreenLabel("home / 首页", x, y - 34);
  const { screen } = screenShell("home", x, y, "WeChat Mini Program", "宠物海报");
  text(screen, "hero title", "上传宠物照片", 24, 122, 260, {
    size: 28,
    lineHeight: 34,
    font: FONTS.extraBold,
    color: COLORS.primary
  });
  text(screen, "hero copy", "1-9 张原图，下一步选择后台海报模板。", 24, 164, 300, {
    size: 14,
    lineHeight: 20,
    font: FONTS.regular,
    color: COLORS.primaryMuted
  });

  const panel = frame(screen, "upload panel", 20, 210, 350, 440, {
    fill: COLORS.surface,
    radius: RADIUS.xl,
    effects: shadow("sm"),
    clipsContent: true
  });
  const preview = frame(panel, "upload preview", 20, 20, 310, 118, {
    fills: [gradient("#fff6ee", "#f5dfcf", COLORS.blueLight)],
    radius: RADIUS.lg,
    clipsContent: true
  });
  petFace(preview, 110, 24, 0.92, { ear: COLORS.brandLight, face: COLORS.surface });
  rect(preview, "count chip", 196, 16, 96, 30, { fill: COLORS.surface, radius: RADIUS.pill, opacity: 0.92 });
  text(preview, "count text", "已选择 4 / 9", 206, 23, 78, {
    size: 12,
    lineHeight: 16,
    font: FONTS.semibold,
    color: COLORS.brand
  });
  pawMark(preview, 26, 70, 30, COLORS.teal);

  const gridX = 20;
  const gridY = 158;
  const gap = 10;
  for (let i = 0; i < 9; i += 1) {
    const col = i % 3;
    const row = Math.floor(i / 3);
    const state = i < 4 ? "photo" : i === 4 ? "add" : "empty";
    drawPhotoSlot(panel, i, gridX + col * (98 + gap), gridY + row * (98 + gap), state);
  }

  const chooseStyleButton = primaryButton(screen, "cta / choose style", "选择海报风格", 20, 670, 350);
  const tabs = tabbar(screen, "home");
  return { screen, chooseStyleButton, mineTab: tabs.mine };
}

function drawStyle(x, y) {
  addScreenLabel("style / 风格选择", x, y - 34);
  const { screen, back } = screenShell("style", x, y, "Poster Style", "选择风格", { back: true });
  text(screen, "section title", "海报风格", 24, 120, 180, {
    size: 22,
    lineHeight: 28,
    font: FONTS.bold,
    color: COLORS.primary
  });
  text(screen, "section copy", "展示图由后台维护，可持续上新。", 24, 151, 270, {
    size: 13,
    lineHeight: 18,
    font: FONTS.regular,
    color: COLORS.primaryMuted
  });
  categoryPill(screen, "全部", 24, 190, true, 58);
  categoryPill(screen, "杂志封面", 92, 190, false, 86);
  categoryPill(screen, "写真馆", 188, 190, false, 70);
  categoryPill(screen, "贴纸拼贴", 268, 190, false, 86);

  const card1 = drawPosterCard(screen, "style card / magazine selected", 24, 246, 342, 206, {
    large: true,
    selected: true,
    title: "城市杂志封面",
    desc: "后台图片 · 推荐展示位",
    gradient: gradient("#342d28", "#b67355", COLORS.brandLight),
    accent: COLORS.teal
  });
  drawPosterCard(screen, "style card / studio", 24, 468, 164, 188, {
    title: "自然写真馆",
    desc: "竖版海报",
    gradient: gradient("#f7f1e8", "#c8916e", COLORS.tealLight),
    ear: COLORS.teal
  });
  drawPosterCard(screen, "style card / collage", 202, 468, 164, 188, {
    title: "潮流拼贴",
    desc: "多图友好",
    gradient: gradient("#fbf7ee", "#8da6e2", COLORS.brandLight),
    accent: COLORS.lavender,
    dot: COLORS.brand
  });

  const note = frame(screen, "config note", 24, 674, 342, 74, {
    fill: COLORS.surface,
    radius: RADIUS.lg,
    stroke: COLORS.border,
    effects: shadow("xs")
  });
  rect(note, "bookmark bg", 16, 17, 40, 40, { fill: COLORS.blueLight, radius: RADIUS.md });
  rect(note, "bookmark", 28, 26, 16, 22, { fill: COLORS.blue, radius: 4 });
  text(note, "note title", "后台配置风格位", 68, 14, 180, {
    size: 14,
    lineHeight: 20,
    font: FONTS.semibold,
    color: COLORS.primary
  });
  text(note, "note copy", "节日和会员专属分组可继续扩展。", 68, 38, 220, {
    size: 12,
    lineHeight: 16,
    font: FONTS.regular,
    color: COLORS.primaryMuted
  });

  const bottom = frame(screen, "bottom action bar", 0, SCREEN.height - SCREEN.bottomBar, SCREEN.width, SCREEN.bottomBar, {
    fill: COLORS.surface,
    stroke: COLORS.border,
    effects: shadow("sm")
  });
  const generateButton = primaryButton(bottom, "cta / generate", "用这个风格生成", 20, 18, 350);
  return { screen, back, card1, generateButton };
}

function drawGenerating(x, y) {
  addScreenLabel("generating / 生成中", x, y - 34);
  const { screen, back } = screenShell("generating", x, y, "Generating", "生成中", { back: true });
  const stage = frame(screen, "poster stage", 35, 128, 320, 428, {
    fills: [gradient("#2f2a30", "#b67355", COLORS.blue)],
    radius: RADIUS.xxl,
    clipsContent: true,
    effects: shadow("xl")
  });
  ellipse(stage, "particle 1", 42, 42, 8, 8, { fill: COLORS.surface, opacity: 0.76 });
  ellipse(stage, "particle 2", 244, 58, 6, 6, { fill: COLORS.tealLight, opacity: 0.78 });
  ellipse(stage, "particle 3", 278, 176, 10, 10, { fill: COLORS.brandTint, opacity: 0.65 });
  ellipse(stage, "particle 4", 64, 250, 7, 7, { fill: COLORS.blueLight, opacity: 0.72 });
  ellipse(stage, "particle 5", 220, 324, 6, 6, { fill: COLORS.surface, opacity: 0.5 });
  rect(stage, "poster line 1", 52, 286, 216, 10, { fill: COLORS.surface, radius: RADIUS.pill, opacity: 0.54 });
  rect(stage, "poster line 2", 72, 308, 176, 8, { fill: COLORS.surface, radius: RADIUS.pill, opacity: 0.38 });
  rect(stage, "poster line 3", 102, 328, 116, 8, { fill: COLORS.surface, radius: RADIUS.pill, opacity: 0.28 });
  petFace(stage, 105, 112, 1.2, { ear: COLORS.brandLight, face: COLORS.surface });
  text(stage, "poster caption top", "PETPOSTER", 0, 370, 320, {
    size: 15,
    lineHeight: 20,
    font: FONTS.extraBold,
    color: COLORS.surface
  }).textAlignHorizontal = "CENTER";
  text(stage, "poster caption bottom", "城市杂志封面", 0, 392, 320, {
    size: 12,
    lineHeight: 16,
    font: FONTS.medium,
    color: "#fff1e8"
  }).textAlignHorizontal = "CENTER";

  const progress = frame(screen, "progress panel", 24, 582, 342, 142, {
    fill: COLORS.surface,
    radius: RADIUS.xl,
    effects: shadow("sm")
  });
  text(progress, "progress title", "正在生成海报", 22, 20, 220, {
    size: 20,
    lineHeight: 26,
    font: FONTS.bold,
    color: COLORS.primary
  });
  text(progress, "progress copy", "请保持页面打开，预览完成后会自动进入结果页。", 22, 52, 260, {
    size: 13,
    lineHeight: 18,
    font: FONTS.regular,
    color: COLORS.primaryMuted
  });
  rect(progress, "progress track", 22, 92, 258, 11, { fill: COLORS.border, radius: RADIUS.pill });
  rect(progress, "progress fill", 22, 92, 186, 11, { fill: COLORS.brand, radius: RADIUS.pill });
  text(progress, "progress value", "72%", 292, 87, 34, {
    size: 14,
    lineHeight: 20,
    font: FONTS.bold,
    color: COLORS.brand
  });
  return { screen, back, stage };
}

function drawResult(x, y) {
  addScreenLabel("result / 结果页", x, y - 34);
  const { screen, back } = screenShell("result", x, y, "Poster Ready", "生成结果", { back: true });
  const poster = frame(screen, "generated poster", 35, 116, 320, 430, {
    fills: [gradient("#1f2937", "#b67355", COLORS.blue)],
    radius: RADIUS.xxl,
    clipsContent: true,
    effects: shadow("xl")
  });
  text(poster, "poster brand", "PetPoster AI", 24, 24, 140, {
    size: 14,
    lineHeight: 20,
    font: FONTS.semibold,
    color: COLORS.surface
  });
  rect(poster, "category chip", 202, 20, 88, 30, { fill: COLORS.surface, radius: RADIUS.pill, opacity: 0.24 });
  text(poster, "category text", "杂志封面", 202, 27, 88, {
    size: 12,
    lineHeight: 16,
    font: FONTS.semibold,
    color: COLORS.surface
  }).textAlignHorizontal = "CENTER";
  petFace(poster, 104, 132, 1.24, { ear: COLORS.brandLight, face: COLORS.surface });
  text(poster, "poster title", "城市杂志封面", 28, 334, 220, {
    size: 28,
    lineHeight: 34,
    font: FONTS.extraBold,
    color: COLORS.surface
  });
  text(poster, "poster copy", "为这组宠物照片生成的封面预览", 28, 374, 230, {
    size: 13,
    lineHeight: 18,
    font: FONTS.regular,
    color: "#fff1e8"
  });

  const panel = frame(screen, "result panel", 24, 568, 342, 72, {
    fill: COLORS.surface,
    radius: RADIUS.lg,
    effects: shadow("xs")
  });
  text(panel, "panel title", "已完成海报预览", 18, 14, 180, {
    size: 15,
    lineHeight: 20,
    font: FONTS.semibold,
    color: COLORS.primary
  });
  text(panel, "panel copy", "当前为本地模拟结果，可替换为真实 AI 图片。", 18, 39, 220, {
    size: 12,
    lineHeight: 16,
    font: FONTS.regular,
    color: COLORS.primaryMuted
  });
  rect(panel, "saved badge", 250, 20, 72, 32, { fill: COLORS.tealLight, radius: RADIUS.pill });
  ellipse(panel, "saved dot", 262, 31, 9, 9, { fill: COLORS.teal });
  text(panel, "saved text", "已保存", 276, 27, 42, {
    size: 12,
    lineHeight: 16,
    font: FONTS.semibold,
    color: COLORS.teal
  });

  for (let i = 0; i < 4; i += 1) {
    const thumb = frame(screen, `photo thumb / ${i}`, 24 + i * 50, 658, 42, 42, {
      fills: [gradient(i % 2 ? "#e8eefc" : "#fff6eb", i % 2 ? "#d9e4ff" : "#ead7c5")],
      radius: RADIUS.md,
      clipsContent: true,
      effects: shadow("xs")
    });
    petFace(thumb, 4, 5, 0.35, { ear: i % 2 ? COLORS.blue : COLORS.brandLight, face: COLORS.surface });
  }
  rect(screen, "photo more", 224, 658, 42, 42, { fill: COLORS.primary, radius: RADIUS.md, opacity: 0.82 });
  text(screen, "photo more text", "+2", 224, 670, 42, {
    size: 15,
    lineHeight: 20,
    font: FONTS.bold,
    color: COLORS.surface
  }).textAlignHorizontal = "CENTER";

  const save = primaryButton(screen, "action / save", "保存海报", 24, 724, 164, { height: 50 });
  const share = secondaryButton(screen, "action / share", "分享给好友", 202, 724, 164, { height: 50 });
  const regen = secondaryButton(screen, "action / regenerate", "再次生成", 24, 784, 164, { height: 44 });
  const change = secondaryButton(screen, "action / change style", "换风格", 202, 784, 164, { height: 44 });
  return { screen, back, save, share, regen, change };
}

function drawHistory(x, y) {
  addScreenLabel("history / 历史记录", x, y - 34);
  const { screen, back } = screenShell("history", x, y, "History", "生成历史", { back: true });
  const records = [
    { title: "城市杂志封面", meta: "4 张照片 · 今天 10:24", bg: gradient("#342d28", "#b67355", COLORS.brandLight) },
    { title: "自然写真馆", meta: "2 张照片 · 昨天 19:08", bg: gradient("#f7f1e8", "#c8916e", COLORS.tealLight) },
    { title: "潮流拼贴", meta: "6 张照片 · 5月13日", bg: gradient("#fbf7ee", "#8da6e2", COLORS.lavenderLight) },
    { title: "节日礼物卡", meta: "1 张照片 · 5月12日", bg: gradient("#fff2dd", "#d97757", COLORS.teal) }
  ];
  const cards = [];
  records.forEach((record, index) => {
    const y0 = 122 + index * 122;
    const card = frame(screen, `record card / ${index}`, 24, y0, 342, 104, {
      fill: COLORS.surface,
      radius: RADIUS.lg,
      effects: shadow("xs")
    });
    const cover = frame(card, "record cover", 12, 12, 80, 80, {
      fills: [record.bg],
      radius: RADIUS.md,
      clipsContent: true
    });
    petFace(cover, 12, 14, 0.6, { ear: index % 2 ? COLORS.teal : COLORS.brandLight, face: COLORS.surface });
    text(card, "record title", record.title, 108, 18, 160, {
      size: 16,
      lineHeight: 21,
      font: FONTS.semibold,
      color: COLORS.primary
    });
    text(card, "record meta", record.meta, 108, 45, 180, {
      size: 12,
      lineHeight: 16,
      font: FONTS.regular,
      color: COLORS.primaryMuted
    });
    rect(card, "status bg", 108, 68, 62, 24, { fill: COLORS.tealLight, radius: RADIUS.pill });
    ellipse(card, "status dot", 118, 76, 8, 8, { fill: COLORS.teal });
    text(card, "status text", "已完成", 130, 73, 38, {
      size: 11,
      lineHeight: 14,
      font: FONTS.semibold,
      color: COLORS.teal
    });
    text(card, "edit", "重新编辑", 236, 70, 62, {
      size: 12,
      lineHeight: 16,
      font: FONTS.semibold,
      color: COLORS.brand
    });
    text(card, "chevron", "›", 312, 39, 14, {
      size: 24,
      lineHeight: 28,
      font: FONTS.bold,
      color: COLORS.primaryMuted
    });
    cards.push(card);
  });
  return { screen, back, firstRecord: cards[0] };
}

function menuRow(parent, id, iconFill, title, copy, x, y) {
  const row = frame(parent, `menu row / ${id}`, x, y, 342, 72, {
    fill: COLORS.surface,
    radius: RADIUS.md,
    stroke: COLORS.border,
    effects: shadow("xs")
  });
  rect(row, "icon bg", 16, 16, 40, 40, { fill: iconFill, radius: RADIUS.md });
  pawMark(row, 24, 23, 24, id === "history" ? COLORS.brand : id === "credits" ? COLORS.warning : COLORS.blue);
  text(row, "title", title, 70, 15, 180, {
    size: 15,
    lineHeight: 20,
    font: FONTS.semibold,
    color: COLORS.primary
  });
  text(row, "copy", copy, 70, 38, 190, {
    size: 12,
    lineHeight: 16,
    font: FONTS.regular,
    color: COLORS.primaryMuted
  });
  text(row, "chevron", "›", 314, 24, 14, {
    size: 22,
    lineHeight: 26,
    font: FONTS.bold,
    color: COLORS.primaryMuted
  });
  return row;
}

function drawMine(x, y) {
  addScreenLabel("mine / 个人中心", x, y - 34);
  const { screen } = screenShell("mine", x, y, "Account", "我的");
  const profile = frame(screen, "profile panel", 24, 120, 342, 112, {
    fill: COLORS.surface,
    radius: RADIUS.xl,
    effects: shadow("sm")
  });
  ellipse(profile, "avatar", 18, 22, 68, 68, { fill: COLORS.brandTint });
  text(profile, "avatar letter", "P", 18, 35, 68, {
    size: 28,
    lineHeight: 34,
    font: FONTS.extraBold,
    color: COLORS.brand
  }).textAlignHorizontal = "CENTER";
  text(profile, "name", "未登录用户", 102, 27, 140, {
    size: 18,
    lineHeight: 24,
    font: FONTS.bold,
    color: COLORS.primary
  });
  text(profile, "copy", "登录后同步生成历史、充值记录与个人资料。", 102, 57, 188, {
    size: 12,
    lineHeight: 17,
    font: FONTS.regular,
    color: COLORS.primaryMuted
  });
  rect(profile, "edit bg", 296, 34, 34, 34, { fill: COLORS.gray50, radius: RADIUS.pill });
  rect(profile, "edit line", 306, 50, 14, 3, { fill: COLORS.primaryMuted, radius: 2 });
  ellipse(profile, "edit dot", 320, 44, 4, 4, { fill: COLORS.brand });

  const summary = frame(screen, "summary grid", 24, 248, 342, 86, {
    fill: COLORS.surface,
    radius: RADIUS.xl,
    effects: shadow("xs")
  });
  [
    ["12", "生成海报"],
    ["38", "剩余次数"],
    ["8", "已保存"]
  ].forEach((item, index) => {
    const x0 = 14 + index * 106;
    text(summary, `summary value / ${index}`, item[0], x0, 17, 102, {
      size: 22,
      lineHeight: 28,
      font: FONTS.extraBold,
      color: index === 1 ? COLORS.brand : COLORS.primary
    }).textAlignHorizontal = "CENTER";
    text(summary, `summary label / ${index}`, item[1], x0, 51, 102, {
      size: 12,
      lineHeight: 16,
      font: FONTS.medium,
      color: COLORS.primaryMuted
    }).textAlignHorizontal = "CENTER";
  });

  text(screen, "menu title", "账户与记录", 24, 360, 180, {
    size: 18,
    lineHeight: 24,
    font: FONTS.bold,
    color: COLORS.primary
  });
  const history = menuRow(screen, "history", COLORS.brandTint, "生成历史", "查看已生成的海报记录", 24, 396);
  const credits = menuRow(screen, "credits", COLORS.warningLight, "充值记录", "次数购买与消费明细", 24, 480);
  menuRow(screen, "profile", COLORS.blueLight, "个人信息设置", "昵称、头像与隐私设置", 24, 564);

  text(screen, "recent title", "最近生成", 24, 666, 120, {
    size: 18,
    lineHeight: 24,
    font: FONTS.bold,
    color: COLORS.primary
  });
  text(screen, "recent link", "查看全部", 304, 670, 62, {
    size: 13,
    lineHeight: 18,
    font: FONTS.semibold,
    color: COLORS.brand
  });
  drawPosterCard(screen, "recent / magazine", 24, 704, 112, 116, {
    title: "杂志",
    desc: "今天",
    gradient: gradient("#342d28", "#b67355"),
    radius: RADIUS.lg
  });
  drawPosterCard(screen, "recent / studio", 150, 704, 112, 116, {
    title: "写真",
    desc: "昨天",
    gradient: gradient("#f7f1e8", "#c8916e"),
    radius: RADIUS.lg,
    ear: COLORS.teal
  });
  drawPosterCard(screen, "recent / collage", 276, 704, 112, 116, {
    title: "拼贴",
    desc: "5月13日",
    gradient: gradient("#fbf7ee", "#8da6e2"),
    radius: RADIUS.lg,
    ear: COLORS.blue
  });

  const tabs = tabbar(screen, "mine");
  return { screen, history, credits, homeTab: tabs.home };
}

async function connect(node, destination, navigation = "NAVIGATE") {
  if (!node || !destination || typeof node.setReactionsAsync !== "function") return;
  try {
    await node.setReactionsAsync([
      {
        trigger: { type: "ON_CLICK" },
        actions: [
          {
            type: "NODE",
            destinationId: destination.id,
            navigation,
            transition: {
              type: "SMART_ANIMATE",
              easing: { type: "EASE_OUT" },
              duration: 0.22
            },
            preserveScrollPosition: false
          }
        ]
      }
    ]);
    created.prototypeNodes.push(node.id);
  } catch (error) {
    created.prototypeNodes.push(`prototype-skipped:${node.name}:${error.message}`);
  }
}

async function buildPrototypeLinks(screens) {
  await connect(screens.home.chooseStyleButton, screens.style.screen);
  await connect(screens.home.mineTab, screens.mine.screen);
  await connect(screens.style.back, screens.home.screen);
  await connect(screens.style.generateButton, screens.generating.screen);
  await connect(screens.style.card1, screens.generating.screen);
  await connect(screens.generating.back, screens.style.screen);
  await connect(screens.generating.stage, screens.result.screen);
  await connect(screens.result.back, screens.generating.screen);
  await connect(screens.result.regen, screens.generating.screen);
  await connect(screens.result.change, screens.style.screen);
  await connect(screens.result.save, screens.mine.screen);
  await connect(screens.history.back, screens.mine.screen);
  await connect(screens.history.firstRecord, screens.result.screen);
  await connect(screens.mine.history, screens.history.screen);
  await connect(screens.mine.homeTab, screens.home.screen);
}

async function main() {
  FONTS = await pickFonts();
  let page = figma.root.children.find((item) => item.name === PAGE_NAME);
  if (!page) {
    page = figma.createPage();
    page.name = PAGE_NAME;
    created.pages.push(page.id);
  }
  await figma.setCurrentPageAsync(page);
  [...page.children].forEach((child) => child.remove());

  await ensureStyles();
  await ensureVariables();

  text(figma.currentPage, "page title", "PetPoster AI 微信小程序 UI", 40, 36, 620, {
    size: 30,
    lineHeight: 38,
    font: FONTS.extraBold,
    color: COLORS.primary
  });
  text(figma.currentPage, "page subtitle", "温暖高级视觉方向 · 6 个高保真画板 · 可点击 prototype 主流程", 40, 78, 720, {
    size: 14,
    lineHeight: 20,
    font: FONTS.regular,
    color: COLORS.primaryMuted
  });

  createComponentLibrary(40, 130);

  const firstRowY = 540;
  const secondRowY = 1430;
  const colX = [40, 480, 920];
  const screens = {
    home: drawHome(colX[0], firstRowY),
    style: drawStyle(colX[1], firstRowY),
    generating: drawGenerating(colX[2], firstRowY),
    result: drawResult(colX[0], secondRowY),
    history: drawHistory(colX[1], secondRowY),
    mine: drawMine(colX[2], secondRowY)
  };

  await buildPrototypeLinks(screens);

  const screenNodes = Object.values(screens).map((item) => item.screen);
  figma.currentPage.selection = screenNodes;
  figma.viewport.scrollAndZoomIntoView(screenNodes);

  return {
    pageId: page.id,
    screenIds: screenNodes.map((node) => node.id),
    componentCount: created.components.length,
    prototypeNodeCount: created.prototypeNodes.filter((item) => !String(item).startsWith("prototype-skipped")).length,
    skipped: created.prototypeNodes.filter((item) => String(item).startsWith("prototype-skipped")),
    variableCount: created.variables.length
  };
}

let FONTS;
main()
  .then((summary) => {
    figma.closePlugin(
      `PetPoster AI Mini Program created: ${summary.screenIds.length} screens, ${summary.componentCount} components, ${summary.prototypeNodeCount} prototype links.`
    );
  })
  .catch((error) => {
    figma.closePlugin(`PetPoster AI generation failed: ${error.message}`);
  });
