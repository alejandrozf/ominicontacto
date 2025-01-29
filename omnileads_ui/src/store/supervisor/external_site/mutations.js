export default {
    initExternalSites (state, sites) {
        state.externalSites = sites;
    },
    initExternalSiteDetail (state, site) {
        state.externalSiteDetail = site;
    },
    initExternalSitesDynamicList(state, sites) {
        console.log('----', sites)
        state.externalSitesDynamicList = sites.filter(item => item.disparador === 5);
    }

};
