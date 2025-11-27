export { RequestError } from './RequestError'

import { AuthApi } from './auth'
import { SitesApi } from './sites'
import { ReviewsApi } from './sites/reviews'
import { TagsApi } from './tags'
import { UserApi } from './user'
import { FlagsApi } from './flags'

interface ApiStore {
  sites?: SitesApi
  siteReviews?: ReviewsApi[]
  user?: UserApi
  tags?: TagsApi
  auth?: AuthApi
  flags?: FlagsApi
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
  getAuthApi() {
    return store.auth || (store.auth = new AuthApi())
  },
  getFlagsApi() {
    return store.flags || (store.flags = new FlagsApi())
  }
}

export type * from './types'
