Meta:
@storyId cxMbrDesignerActivity.story

Narrative:
In order to create master batch records
As an MBR designer
I want to assign CX definitions to activities in the MBR Designer


Scenario: CX definitions can be assigned to and removed from activities

Given The CX MBR 'SimpleMbr' is imported
And The MBR Administration is opened
And The CX definition with ID 'CxDefBoolean' is used by the equipment type with ID 'CXEQT'
When The refresh button is clicked in the main toolbar
And A search is executed for string 'SimpleMbr'
And The update button is clicked in the main toolbar
And The MBR Designer is opened
And The node 'Basic operation (BO1)' is selected in the MBR structure
And The step 'CBF1' is selected in the diagram of 'Basic operation'
And The edit button is clicked in the CBF's detail area activity tab
And The activity type 'Measured value' is selected and valid data is entered
And The tab 'CX definitions (4)' in the 'Activity' dialog field is selected
Then In the dialog 'Activity' the 'deleteCxDefinition' button is 'disabled'

When In the dialog 'Activity' the 'selectCxDefinitionFromAll' button is clicked
And In the dialog 'selection' the 'apply' button is clicked
And CX definition 'CxDefNumber' is selected
And The 'OK' button is clicked in the current dialog
Then The list of CX definitions assigned to the activity contains the following data:
| ID           | Description                  |
| CxDefNumber  | Description for CxDefNumber  |
And In the dialog 'Activity' the 'deleteCxDefinition' button is 'enabled'

When In the dialog 'Activity' the 'selectCxDefinitionFromAll' button is clicked
And In the dialog 'selection' the 'apply' button is clicked
And CX definition 'CxDefBoolean' is selected
And The 'OK' button is clicked in the current dialog
Then The list of CX definitions assigned to the activity contains the following data:
| ID           | Description                  |
| CxDefBoolean | Description for CxDefBoolean |
| CxDefNumber  | Description for CxDefNumber  |
And In the dialog 'Activity' the 'deleteCxDefinition' button is 'enabled'

When In the dialog 'Activity' the 'deleteCxDefinition' button is clicked
Then The list of CX definitions assigned to the activity contains the following data:
| ID           | Description                  |
| CxDefBoolean | Description for CxDefBoolean |
And In the dialog 'Activity' the 'deleteCxDefinition' button is 'enabled'

When In the dialog 'Activity' the 'deleteCxDefinition' button is clicked
Then In the dialog 'Activity' the 'deleteCxDefinition' button is 'disabled'