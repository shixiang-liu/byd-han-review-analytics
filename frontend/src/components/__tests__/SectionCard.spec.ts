import { mount } from "@vue/test-utils";
import { describe, expect, it } from "vitest";
import SectionCard from "../SectionCard.vue";

describe("SectionCard", () => {
  it("renders the header, toolbar, and action slots", () => {
    const wrapper = mount(SectionCard, {
      props: {
        eyebrow: "Overview",
        title: "Decision hub",
        subtitle: "Shared presentation shell",
      },
      slots: {
        toolbar: "<button>Refresh</button>",
        actions: "<a href='#'>View all</a>",
        default: "<p>Body content</p>",
      },
    });

    expect(wrapper.text()).toContain("Overview");
    expect(wrapper.text()).toContain("Decision hub");
    expect(wrapper.text()).toContain("Shared presentation shell");
    expect(wrapper.text()).toContain("Refresh");
    expect(wrapper.text()).toContain("View all");
    expect(wrapper.text()).toContain("Body content");
  });
});
