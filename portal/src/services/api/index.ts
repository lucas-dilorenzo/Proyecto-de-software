export { RequestError } from './RequestError'

import { AuthApi } from './auth'
import { SitesApi } from './sites'
import { ReviewsApi } from './sites/reviews'
import { UserApi } from './user'

interface ApiStore {
  sites?: SitesApi
  siteReviews?: ReviewsApi[]
  user?: UserApi
  auth?: AuthApi
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
  getAuthApi() {
    return store.auth || (store.auth = new AuthApi())
  },
}

export type * from './types'
