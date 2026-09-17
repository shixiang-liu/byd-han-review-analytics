import { mount } from "@vue/test-utils";
import { describe, expect, it, vi } from "vitest";
import HighlightPanel from "../HighlightPanel.vue";

describe("HighlightPanel", () => {
  it("renders the conclusion summary and highlights", () => {
    const wrapper = mount(HighlightPanel, {
      props: {
        eyebrow: "Key conclusion",
        title: "Focus on the Q2 segment",
        summary: "The strongest opportunity sits in the high-value, high-priority quadrant.",
        highlights: ["Priority rank 1", "Confidence: high", "Action: increase allocation"],
        tone: "critical",
      },
    });

    expect(wrapper.text()).toContain("Key conclusion");
    expect(wrapper.text()).toContain("Focus on the Q2 segment");
    expect(wrapper.text()).toContain("The strongest opportunity sits in the high-value, high-priority quadrant.");
    expect(wrapper.text()).toContain("Priority rank 1");
    expect(wrapper.text()).toContain("Confidence: high");
    expect(wrapper.classes()).toContain("highlight-panel--critical");
  });

  it("does not emit duplicate key warnings for repeated highlights", () => {
    const warn = vi.spyOn(console, "warn").mockImplementation(() => {});

    try {
      const wrapper = mount(HighlightPanel, {
        props: {
          title: "Duplicate text is allowed",
          summary: "Repeated labels should render without key collisions.",
          highlights: ["Shared insight", "Shared insight"],
        },
      });

      expect(wrapper.findAll(".highlight-panel__item")).toHaveLength(2);
      expect(warn).not.toHaveBeenCalled();
    } finally {
      warn.mockRestore();
    }
  });
});
