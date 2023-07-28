<template>
  <div class="fit row justify-center">
     <job-card :job="job" v-for="job of jobs" :key="job.id"/>

     <q-page-sticky position="bottom-right" :offset="[18, 18]">
        <q-btn fab icon="add" color="accent" @click="$refs.jobDialog.show()"/>
        <job-dialog ref="jobDialog" />
     </q-page-sticky>
  </div>
</template>

<script>
import {ref, defineComponent } from 'vue'
import { storeToRefs } from 'pinia'
import JobCard from 'components/JobCardComponent.vue'
import JobDialog from 'components/JobDialogComponent.vue'
import { useJobStore } from 'stores/jobStore'



export default defineComponent({
  name: 'JobsPage',

  components: {
    JobCard, JobDialog
  },

  methods: {
  },

  setup() {
     const store = useJobStore()
     store.loadJobs()

     const {jobs} = storeToRefs(store)

     return {
        jobs
     }
  },

  data() {
     return {
     }
  }

})
</script>
