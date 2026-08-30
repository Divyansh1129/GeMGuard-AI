import api from "./api";
import bidderService from "./bidderService";

function mapTender(tender, bidders = []) {
  const linkedBidders = bidders.filter((bidder) => bidder.tenderId === tender.id);
  return {
    ...tender,
    totalBids: linkedBidders.length,
    verified: linkedBidders.filter((bidder) => bidder.status === "Verified").length,
    underReview: linkedBidders.filter((bidder) => ["Review Required", "Incomplete"].includes(bidder.status)).length,
    flagged: linkedBidders.filter((bidder) => bidder.status === "Non-Compliant").length,
  };
}

export const tenderService = {
  async getAll() {
    const [{ data: tenders }, bidders] = await Promise.all([
      api.get("/dashboard/tenders"),
      bidderService.getAll(),
    ]);
    return tenders.map((tender) => mapTender(tender, bidders));
  },

  async getById(id) {
    try {
      const [{ data: tender }, bidders] = await Promise.all([
        api.get(`/dashboard/tenders/${encodeURIComponent(id)}`),
        bidderService.getByTender(id),
      ]);
      return mapTender(tender, bidders);
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
    return mapTender(data, []);
  },
};

export default tenderService;