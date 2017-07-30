/* global Vue, $, bb */

// single chart: https://vuejs.org/v2/guide/routing.html

Vue.component('source-description', {
  template: '#sources-template',
  props: ['source'],
});

// use vm for console debugging
// eslint-disable-next-line no-unused-vars
const vm = new Vue({
  el: '#app',

  data: {
    stats: {},
  },

  created() {
    $.ajax('https://s3.amazonaws.com/ragtag-fftf/by_source.json').then((resp) => {
      this.$data.stats = resp;
    });
  },

  computed: {
    positiveSources: function posSrc() {
      return this.sourcesArray('positive');
    },

    negativeSources: function negSrc() {
      return this.sourcesArray('negative');
    },
  },

  methods: {
    sourcesArray: function sourcesArray(sentiment) {
      if (!this.$data.stats.sources) {
        return [];
      }

      const icons = { bot: 'fa-server', form: 'fa-bullhorn', individual: 'fa-user-circle-o' };
      const sources = this.$data.stats.sources;
      const srcList = [];

      Object.keys(sources).forEach((key) => {
        if (sources[key].sentiment === sentiment) {
          sources[key].count = (this.$data.stats[`${sentiment}_by_source`][key] || 0).toLocaleString();
          sources[key].iconClass = icons[sources[key].icon] || 'fa-user-circle-o';
          sources[key].id = key;
          srcList.push(sources[key]);
        }
      });

      return srcList;
    },

    toChartColumns: function toChartColumns(sources, counts) {
      // have { source1: { unbreached: 10, breached: 110}}
      // want { unbreached: [ 10, 20, 300], breached: [ 110, 220, 30]}
      // and [source1, source2, source3]
      const columns = { breached: [], unbreached: [] };
      const sourcesWithData = [];

      sources.forEach((source) => {
        console.log('source=', source, ' counts=', counts[source]);
        if (!counts[source]) {
          return;
        }
        sourcesWithData.push(source);
        const breached = counts[source].breached || 0;
        const unbreached = counts[source].unbreached || 0;
        const total = breached + unbreached;

        columns.unbreached.push(Math.round((unbreached / total) * 100));
        columns.breached.push(Math.round((breached / total) * 100));
      });

      return { columns, sources: sourcesWithData };
    },

    breachedChart: function breachedChart(id, data, sources) {
      const breached = this.$data.stats.breached;
      const options = {
        bindto: id,
        data: {
          order: false,
          type: 'bar',
          colors: {
            breached: '#d7191c',
            unbreached: '#abd9e9',
          },
          labels: {
            format: function labelFmt(v) {
              return `${v}%`;
            },
          },
          columns: [
            ['breached'].concat(data.breached),
            ['unbreached'].concat(data.unbreached),
          ],
          groups: [
            ['breached', 'unbreached'],
          ],
        },
        tooltip: {
          format: {
            title: function title(d) {
              const source = sources[d];

              if (breached[source]) {
                const total = (breached[source].breached || 0) +
                  (breached[source].unbreached || 0);

                return `${source} - ${d3.format(',')(total)} commentsmorage`;
              }

              return source;
            },
          },
        },
        axis: {
          rotated: true,
          y: {
            max: 90,
            tick: {
              format: function labelFmt(v) {
                return `${v}%`;
              },
            },
          },
          x: {
            type: 'category',
            categories: sources,
          },
        },
      };

      bb.generate(options);
    },
  },

  watch: {
    stats: function updateStats() {
      const counts = this.$data.stats.breached;
      const sources = this.$data.stats.sources;
      const positiveSources = Object.keys(sources).filter(src => sources[src].sentiment === 'positive');
      const negativeSources = Object.keys(sources).filter(src => sources[src].sentiment === 'negative');
      const negative = this.toChartColumns(negativeSources, counts);
      const positive = this.toChartColumns(positiveSources, counts);

      this.breachedChart('#breachedNegative', negative.columns, negative.sources);
      this.breachedChart('#breachedPositive', positive.columns, positive.sources);
    /*
    labels from source.json
    tooltip shows sample size
    click label shows sample with totals
    */
    },
  },
});
