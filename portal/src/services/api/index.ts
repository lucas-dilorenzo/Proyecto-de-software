export { RequestError } from './RequestError'

import { SitesApi } from './sites'
import { ReviewsApi } from './sites/reviews'
import { TagsApi } from './tags'
import { UserApi } from './user'

interface ApiStore {
  sites?: SitesApi
  siteReviews?: ReviewsApi[]
  user?: UserApi
  tags?: TagsApi
}
const store: ApiStore = {}

export default {
  getSitesApi() {
    return store.sites || (store.sites = new SitesApi())
  },
  getSiteReviewsApi(siteId: number) {
    if (!store.siteReviews) {
      store.siteReviews = []
    }
    return store.siteReviews[siteId] || (store.siteReviews[siteId] = new ReviewsApi(siteId))
  },
  getUserApi() {
    return store.user || (store.user = new UserApi())
  },
  getTagsApi() {
    return store.tags || (store.tags = new TagsApi())
  },
}

export type * from './types'
