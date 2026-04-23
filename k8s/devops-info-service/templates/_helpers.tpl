{{/* Common environment variables used by the app container. */}}
{{- define "devops-info-service.envVars" -}}
- name: PORT
  value: {{ .Values.service.targetPort | quote }}
- name: HOST
  value: {{ .Values.env.host | quote }}
- name: CONFIG_FILE
  value: {{ printf "%s/%s" .Values.config.mountPath .Values.config.fileName | quote }}
- name: VISITS_FILE
  value: {{ printf "%s/%s" .Values.persistence.mountPath .Values.persistence.visitsFileName | quote }}
{{- end -}}

{{/* Vault Agent Injector annotations for file-based secret rendering. */}}
{{- define "devops-info-service.vaultAnnotations" -}}
vault.hashicorp.com/agent-inject: "true"
vault.hashicorp.com/role: {{ .Values.vault.role | quote }}
vault.hashicorp.com/agent-inject-secret-{{ .Values.vault.renderedFileName }}: {{ .Values.vault.secretPath | quote }}
vault.hashicorp.com/agent-inject-template-{{ .Values.vault.renderedFileName }}: |
  {{`{{- with secret "`}}{{ .Values.vault.secretPath }}{{`" -}}`}}
  APP_USERNAME={{`{{ .Data.data.username }}`}}
  APP_PASSWORD={{`{{ .Data.data.password }}`}}
  APP_DB_URL={{`{{ .Data.data.db_url }}`}}
  APP_API_KEY={{`{{ .Data.data.api_key }}`}}
  {{`{{- end -}}`}}
{{- if .Values.vault.agentInjectCommand }}
vault.hashicorp.com/agent-inject-command-{{ .Values.vault.renderedFileName }}: {{ .Values.vault.agentInjectCommand | quote }}
{{- end }}
{{- end -}}