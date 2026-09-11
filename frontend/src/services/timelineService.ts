import { API } from "@/constants/api-endpoints";
import { api } from "@/lib/api-client";
import { TimelineEvent, TimelineQuery } from "@/types/timeline";

export const timelineService = {
  list: (params: TimelineQuery = {}): Promise<TimelineEvent[]> => {
    const query = new URLSearchParams();
    if (params.case_id) query.set("case_id", params.case_id);
    if (params.limit) query.set("limit", String(params.limit));
    const qs = query.toString();
    return api.get<TimelineEvent[]>(
      qs ? `${API.timeline.list}?${qs}` : API.timeline.list,
    );
  },
};
