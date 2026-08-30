import api from "./api";

function mapTender(tender) {
  return {
    ...tender,
    deadline: "Not extracted",
    value: "Not extracted",
    totalBids: 0,
    verified: 0,
    underReview: 0,
    flagged: 0,
  };
}

export const tenderService = {
  async getAll() {
    const { data } = await api.get("/dashboard/tenders");
    return data.map(mapTender);
  },
  async getById(id) {
    try {
      const { data } = await api.get(`/dashboard/tenders/${encodeURIComponent(id)}`);
      return mapTender(data);
    } catch {
      return null;
    }
  },
  async upload({ name, department, file }) {
    const form = new FormData();
    form.append("name", name);
    form.append("department", department || "");
    form.append("file", file);
    const { data } = await api.post("/dashboard/tenders/upload", form, true);
    return mapTender(data);
  },
};

export default tenderService;
