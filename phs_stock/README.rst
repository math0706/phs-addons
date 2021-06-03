## Create cron to create automatically batch transfer

Action Name: name of the cron
Model: Rules to create picking batch
Execute Every: 1 Days
Next Execution Date: set the next execution at 11:00
Python Code: model.search([('name', '=', name_of_the_rule)]).batch_creation(True)
