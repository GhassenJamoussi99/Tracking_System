#!/bin/bash

RESSOURCE_FILE_1="assets/ressources_rc.py"
RESSOURCE_FILE_2="assets/imgs_rc.py"

PY_UI_FILE="views/mainwindow_view_ui.py"

cd presentation_layer/

###################################################################################
echo "Converting the ressources.qrc to ressources_rc.py..."

pyrcc5 assets/ressources.qrc -o assets/ressources_rc.py && \
echo "Converting ressources.qrc to ressources_rc.py was successfull ✓" \
|| echo "Converting ressources.qrc to ressources_rc.py failed ✘"

sleep 1
echo 
###################################################################################
echo "Converting the new ui to a python file..."

pyuic6 -x mainwindow.ui -o views/mainwindow_view_ui.py && \
echo "Converting the ui to py was successfull ✓" || \
echo "Converting the ui to py failed ✘"

sleep 1
echo 
###################################################################################
# Check if the file exists

# Function to replace import statement
replace_import() {
    local FILE="$1"
    
    # Check if the file exists
    if [[ -f "$FILE" ]]; then
        # Check if the line to replace exists in the file
        if grep -q 'from PyQt5 import QtCore' "$FILE"; then
            # Perform the replacement
            sed -i 's/from PyQt5 import QtCore/from PyQt6 import QtCore/g' "$FILE"
            echo "Import statement replaced successfully in $FILE."
        else
            echo "No 'from PyQt5 import QtCore' statement found in $FILE. No changes made."
        fi
    else
        echo "File $FILE does not exist."
        exit 1
    fi
}

# Replace import statement in both files
replace_import "$RESSOURCE_FILE_1"
replace_import "$RESSOURCE_FILE_2"

###################################################################################
IMPORT_STATEMENT="import presentation_layer.assets.ressources_rc"

# Check if the file exists
if [[ -f "$PY_UI_FILE" ]]; then
    # Create a temporary file
    TEMP_FILE=$(mktemp)

    # Write the import statement into the temporary file
    echo "$IMPORT_STATEMENT" > "$TEMP_FILE"

    # Append the original file contents to the temporary file
    cat "$PY_UI_FILE" >> "$TEMP_FILE"

    # Move the temporary file to overwrite the original file
    mv "$TEMP_FILE" "$PY_UI_FILE"

    echo "Import statement added successfully."
else
    echo "File $PY_UI_FILE does not exist."
fi
