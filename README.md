### Style Shop Module

Ability to style shop by overriding css


## Usage

Add custom styling to jamla.yaml file  
(TODO: Ability to set this from the dashboard)

Custom styling is applied by adding a "options->stlyes" entry
under the theme section of your jamla.yaml file. 

Styles entered will be injected into the base of the template
output as inline css using <style> tags.

Example valid entry:
 
``` 
  theme:
  name: jesmond
  options: 
    styles:
      - selector: body
        rules: 
          - color: red
          - background: orange
      - selector: .kcBlue
        rules:
          - background: black
          - border: 5px solid yellow;
```

