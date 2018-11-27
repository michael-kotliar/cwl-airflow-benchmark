class: Workflow
cwlVersion: v1.0
inputs: []
outputs:
  empty_file:
    type: File?
    outputSource: sleep/empty_file
steps:
  sleep:
    in: []
    out: [empty_file]
    run:
      class: CommandLineTool
      cwlVersion: v1.0
      baseCommand:
        - sleep
        - "3600"
      inputs: []
      outputs:
        empty_file:
          type: File?
          outputBinding:
            glob: "*"