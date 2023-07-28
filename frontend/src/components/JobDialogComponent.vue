<template>
   <q-dialog v-model="visible">
      <q-card style="min-width: 400px">
        <q-item class="text-h6">
          <q-item-section v-if="job_id">
            <q-item-label>Edit job</q-item-label>
            <q-item-label caption>{{ job.id }}</q-item-label>
          </q-item-section>
          <q-item-section v-else>
            <q-item-label>Create a new job</q-item-label>
            <q-item-label caption></q-item-label>
          </q-item-section>
        </q-item>
        <q-item dense class="bg-grey-2 text-subtitle2">Generic</q-item>

        <q-item dense>
          <q-item-section>Spider</q-item-section>
          <q-item-section><q-select dense options-dens
                :disable="!!job_id" :options="spiderNames"
                v-model="job.spider.name"
                @update:model-value="spiderChanged"
          ></q-select></q-item-section>
        </q-item>
        <q-item dense>
          <q-item-section>Schedule</q-item-section>
          <q-item-section><q-input dense v-model="job.trigger"></q-input></q-item-section>
        </q-item>

        <q-separator />
        <q-item dense class="bg-grey-2 text-subtitle2">Parameters</q-item>
        <q-item dense v-for="(param, index) in job.spider.params">
          <q-item-section>{{ param.name }}</q-item-section>
          <q-item-section><q-input dense v-model="job.spider.params[index].value"></q-input></q-item-section>
        </q-item>

        <q-separator />
        <q-item dense class="bg-grey-2 text-subtitle2"><q-item-section>Environment</q-item-section>
                <q-item-section side><q-btn size="12px" flat dense round icon="add" color="grey-9" @click="addSettingsRow"/></q-item-section>
        </q-item>
        <q-item dense v-for="(param, index) in job.spider.settings">
          <q-item-section><q-input clearable dense @clear="job.spider.settings.splice(index,1)" v-model="job.spider.settings[index].name"></q-input></q-item-section>
          <q-item-section><q-input dense v-model="job.spider.settings[index].value"></q-input></q-item-section>
        </q-item>

        <q-separator />
        <q-card-actions align="right">
          <q-btn flat label="Cancel" color="primary" v-close-popup />
          <q-btn flat label="Save" color="primary" v-close-popup @click="saveJob"/>
        </q-card-actions>
      </q-card>
   </q-dialog>
</template>

<script>
import { ref, defineComponent } from 'vue'
import { mapState, mapActions } from 'pinia'
import { useJobStore } from 'stores/jobStore'
import { useSpiderStore } from 'stores/spiderStore'


export default defineComponent({
  name: 'JobDialog',

  props: {
    job_id: {type: String},
  },

  components: {
  },

  computed: {
    ...mapState(useSpiderStore, ['spiderNames'])
  },

  methods: {
    ...mapActions(useJobStore, ['getJobById', 'createJob', 'updateJob']),
    ...mapActions(useSpiderStore, ['spiderByName']),
    mapFromStore(data){
      let job = {
        id: null, spider: { name: null, params: {}, settings: {}}, trigger: null,
        ...data
      }
      if( job.spider.name !== null ){
         let spider = this.spiderByName(job.spider.name)
         let def_params = Object.fromEntries(Object.entries(spider.params).map(([key, value]) => ([key, null])))
         job.spider.params = {...def_params, ...job.spider.params}
      }

      job.spider.params = Object.entries(job.spider.params)
                             .map( ([key, value]) => ({"name": key, "value": value}) )
      job.spider.settings = Object.entries(job.spider.settings)
                              .map( ([key, value]) => ({"name": key, "value": value}) )
      return job
    },
    mapToStore(){
      let data = {
        spider: { name: null, params: {}, settings: {}}, trigger: null,
        ...this.job
      }
      data.spider.params = Object.fromEntries(
          data.spider.params
            .filter((param) => param.name !== null && param.value !== null  )
            .map((param) => ([param.name, param.value]))
      )
      data.spider.settings = Object.fromEntries(
          data.spider.settings
            .filter((param) => param.name !== null && param.value !== null )
            .map((param) => ([param.name, param.value]))
      )
      // remove null keys
      return Object.fromEntries(Object.entries(data).filter(([_, v]) => v != null))
    },
    async show(){
      let job = {}
      if( this.job_id ){
        job = await this.getJobById(this.job_id)
      }
      this.job = this.mapFromStore(job)
      this.visible = true
    },
    spiderChanged(value){
      let spider = this.spiderByName(value)
      this.job.spider.params = Object.entries(spider.params).map(([key, value]) => ({"name": key, "value": null}) )
    },
    addSettingsRow(){
      this.job.spider.settings.push({name: null, value: null})
    },
    async saveJob(){
      const data = this.mapToStore()
      let response = await (this.job_id ? this.updateJob(data) : this.createJob(data))
      this.$q.notify({
          type: 'positive',
          message: 'Job was successfully saved.'
      })
    }
  },

  setup() {
    useSpiderStore().loadSpiders()
  },

  data() {
    return {
      visible: false,
      job: {}
    }
  }

})
</script>
