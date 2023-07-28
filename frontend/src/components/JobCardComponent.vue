<template>
  <div class="q-pa-sm" style="min-width: 360px">
     <q-card flat bordered class="bg-grey-1">
        <q-item class="bg-secondary text-white">
          <q-item-section>
            <q-item-label>{{ job.spider.name }}</q-item-label>
          </q-item-section>
          <q-item-section side>
            <div class="">
              <q-btn size="12px" flat dense round icon="delete" color="grey-9" @click="deleteJob"/>
              <q-btn size="12px" flat dense round icon="play_arrow" color="grey-9" @click="$refs.runDialog.show()"/>
              <q-btn size="12px" flat dense round icon="more_vert" color="grey-9" @click="$refs.editDialog.show()"/>
            </div>
          </q-item-section>
        </q-item>
        <q-separator/>
        <q-list dense>
            <q-item>
              <q-item-section ><q-item-label>Schedule</q-item-label></q-item-section>
              <q-item-section side><q-item-label>{{ job.trigger }}</q-item-label></q-item-section>
            </q-item>

            <q-item>
              <q-item-section ><q-item-label>Next run</q-item-label></q-item-section>
              <q-item-section side><q-item-label>{{ formatDate(job.next_run) }}</q-item-label></q-item-section>
            </q-item>

            <q-separator/>
            <q-item>
              <q-item-section ><q-item-label>Last run</q-item-label></q-item-section>
              <q-item-section side v-if="job.statistics">
                  <q-icon :color="isJobRunSuccess(job)?'positive':'negative'"
                          :name="isJobRunSuccess(job)?'done':'warning'">
                      <q-tooltip>{{ formatDate(job.statistics.start_time) }}</q-tooltip>
                  </q-icon>
              </q-item-section>
            </q-item>

            <q-item>
              <q-item-section ><q-item-label>Scrapped items</q-item-label></q-item-section>
              <q-item-section side v-if="job.statistics">
                 <q-badge rounded color="secondary"
                          :label="job.statistics.item_scraped_count +'/' + (job.statistics.item_scraped_count+job.statistics.item_dropped_count)  " />
              </q-item-section>
            </q-item>

            <q-item>
              <q-item-section ><q-item-label>Requests</q-item-label></q-item-section>
              <q-item-section side v-if="job.statistics">
                  <q-badge rounded :color="isJobRunSuccess(job)?'positive':'negative'"
                  :label="job.statistics.http_success_requests +'/' + job.statistics.http_requests">
                  <q-tooltip>{{ humanize.filesize(job.statistics.response_bytes) }}</q-tooltip></q-badge>
              </q-item-section>
            </q-item>
        </q-list>
     </q-card>

     <q-dialog ref="runDialog">
        <q-card style="min-width: 300px">
          <q-item>
            <q-item-section>
              <q-item-label class="text-h6">Are you sure to run job</q-item-label>
              <q-item-label caption>{{ job.spider.name }}</q-item-label>
            </q-item-section>
          </q-item>
          <q-separator/>

          <q-card-actions align="right">
            <q-btn flat label="Cancel" color="primary" v-close-popup />
            <q-btn flat label="Run" color="primary" v-close-popup @click="runJob(job)"/>
          </q-card-actions>
        </q-card>
     </q-dialog>

     <job-dialog ref="editDialog" :job_id="job.id"></job-dialog>
  </div>
</template>

<script>

import { ref, defineComponent } from 'vue'
import { date, useQuasar } from 'quasar'
import { mapActions } from 'pinia'
import { useJobStore } from 'stores/jobStore'
import JobDialog  from 'components/JobDialogComponent.vue'

var humanize = require('humanize');


export default defineComponent({
  name: 'JobCard',

  props: {
    job: { type: Object },
  },
  components: {
    JobDialog
  },
  computed: {
    formatDate(){
      return (value) => {
          return date.formatDate(value, "DD.MM.YYYY HH:mm:ss")
      }
    },
    isJobRunSuccess(){
      return (job) => {
          return job.statistics !== null && job.statistics.http_requests == job.statistics.http_success_requests;
      }
    }
  },
  methods: {
    ...mapActions(useJobStore, ['startJob', 'removeJob']),
    runJob(job){
      this.startJob(job.id)
      this.$q.notify({
          type: 'positive',
          message: 'Job was successfully started.'
      })
    },
    deleteJob(){
      /*
      this.removeJob(this.job.id)
      this.$q.notify({
          type: 'positive',
          message: 'Job was removed successfully.'
      })
      */
    }
  },
  data() {
    return {}
  },
  setup () {
    return {
      humanize
    }
  }
})
</script>
