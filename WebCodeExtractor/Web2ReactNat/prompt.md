# Prompt
A website is defined in the input files at the location listed in the `Input` section.

Then I want you to generate a markdown file within `C:\Users\ricky\Tools\WebExtractor\Design` called `Design.md` that explains the website content in the following way:
```
# Project Overview
- Name: Name of website
- Framework: What framework is it using, if known
- UI components: What UI libaries are being used

## Description

- General description of website layout and design
## Design Specifics
- Describe the website in the following details:
    - features
    - the design for each feature
    - JavaScript functions used and for what purpose

- General Design Notes:		
    - **Layout**: The prototype uses a vertical scrollable design with a clean, minimalistic aesthetic, featuring a light background with soft gradients.
    - **Typography**: Consistent font styles are used, with bold headings for sections and regular text for details.
    - **Interactivity**: Buttons and links (e.g., "Show more") suggest interactive elements, typical of a Figma prototype meant for user testing or design review.
    - **Color Scheme**: Predominantly light tones with orange accents for buttons, creating a friendly and approachable feel.
    - Error handling:
        - implement comprehensive error handling and log outputs
    - Data fetching in components
        - use React native hooks for data fetching in client-side components. Implement loading states and error handling for all data fetching operations

# Components

- Component
    -  Detailed explanation of the purpose of the component and how it is being built

# Documentation
- here you can add example code that can be referenced to build this app or site

```

## Input
Html: C:\Users\ricky\Tools\WebExtractor\output\html
Css: C:\Users\ricky\Tools\WebExtractor\output\css
Js: C:\Users\ricky\Tools\WebExtractor\output\js

## Output
React Native app
