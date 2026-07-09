export const TASKS = [
  { value: "color_change", label: "包身换色", hint: "只修改包身主体颜色" },
  { value: "material_replace", label: "材质替换", hint: "只替换主体材质质感" },
  { value: "model_showcase", label: "模特展示图", hint: "生成电商模特展示图" }
] as const;

export const VARIABLES = [
  "target_color",
  "target_material",
  "model_showcase_requirement",
  "wearing_method",
  "scene",
  "outfit",
  "output_count",
  "extra_requirements"
];

export const taskLabel = (value: string) => TASKS.find((task) => task.value === value)?.label || value;
