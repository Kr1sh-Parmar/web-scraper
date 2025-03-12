import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from datetime import datetime
import os
import json
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import TimeoutException, NoSuchElementException, ElementNotInteractableException, UnexpectedAlertPresentException
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.alert import Alert

def scrape_soil_wetness_data(longitude, latitude, start_date, end_date):
    """
    Scrape soil wetness index data from MOSDAC website.
    
    Args:
        longitude (str): Longitude value
        latitude (str): Latitude value
        start_date (str): Start date in format DD/MM/YYYY
        end_date (str): End date in format DD/MM/YYYY
        
    Returns:
        DataFrame or dict: The scraped data
    """
    # Set up Chrome options
    chrome_options = Options()
    # Uncomment the line below to run Chrome in headless mode
    # chrome_options.add_argument("--headless")
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("--disable-notifications")
    chrome_options.add_argument("--disable-popup-blocking")
    
    # Initialize the WebDriver
    print("Initializing WebDriver...")
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    
    try:
        # Open the website
        print("Opening the MOSDAC website...")
        driver.get("https://mosdac.gov.in/swi/")
        
        # Take a screenshot of the initial page
        initial_screenshot = "initial_page.png"
        driver.save_screenshot(initial_screenshot)
        print(f"Saved initial page screenshot to {initial_screenshot}")
        
        # Wait for the page to load completely
        print("Waiting for page to fully load...")
        time.sleep(10)  # Increased wait time for page to fully load
        
        # Click on the arrow icon beside "Time Series"
        print("Trying to locate and click on Time Series panel...")
        
        # Multiple approaches to find and click the Time Series element
        time_series_clicked = False
        
        # Method 1: Try to find by XPath containing 'Time Series' text
        try:
            time_series_elements = driver.find_elements(By.XPATH, "//*[contains(text(), 'Time Series')]")
            if time_series_elements:
                print(f"Found {len(time_series_elements)} elements containing 'Time Series' text")
                # Try clicking the first element
                driver.execute_script("arguments[0].click();", time_series_elements[0])
                time_series_clicked = True
                print("Clicked on Time Series (Method 1)")
        except Exception as e:
            print(f"Method 1 failed: {str(e)}")
        
        # Method 2: Try to find the arrow element
        if not time_series_clicked:
            try:
                arrows = driver.find_elements(By.XPATH, "//div[contains(@class, 'arrow')]")
                if arrows:
                    print(f"Found {len(arrows)} possible arrow elements")
                    driver.execute_script("arguments[0].click();", arrows[0])
                    time_series_clicked = True
                    print("Clicked on arrow (Method 2)")
            except Exception as e:
                print(f"Method 2 failed: {str(e)}")
        
        # Method 3: Try to find by class name that might contain expandable panels
        if not time_series_clicked:
            try:
                panels = driver.find_elements(By.CSS_SELECTOR, ".panel, .accordion, .expandable, .collapsible")
                if panels:
                    print(f"Found {len(panels)} possible panel elements")
                    driver.execute_script("arguments[0].click();", panels[0])
                    time_series_clicked = True
                    print("Clicked on panel (Method 3)")
            except Exception as e:
                print(f"Method 3 failed: {str(e)}")
        
        # Take a screenshot after attempting to click Time Series
        time_series_screenshot = "after_time_series_click.png"
        driver.save_screenshot(time_series_screenshot)
        print(f"Saved screenshot after Time Series click attempt to {time_series_screenshot}")
        
        # Wait for any animation to complete
        time.sleep(5)
        
        # Look for form elements or inputs
        print("Analyzing form structure...")
        
        # Execute JavaScript to print out all input fields in the console (for debugging)
        driver.execute_script("""
            var inputs = document.querySelectorAll('input');
            console.log('Found ' + inputs.length + ' input elements:');
            for (var i = 0; i < inputs.length; i++) {
                console.log('Input #' + i + ': type=' + inputs[i].type + 
                          ', id=' + inputs[i].id + 
                          ', name=' + inputs[i].name + 
                          ', placeholder=' + inputs[i].placeholder);
            }
        """)
        
        # Try multiple ways to find and interact with the longitude and latitude inputs
        print("Looking for longitude and latitude inputs...")
        
        # Look for all input fields
        input_fields = driver.find_elements(By.TAG_NAME, "input")
        print(f"Found {len(input_fields)} input fields")
        
        # Take a screenshot of the form
        form_screenshot = "form_view.png"
        driver.save_screenshot(form_screenshot)
        print(f"Saved form view screenshot to {form_screenshot}")
        
        # Print details of each input field
        for i, inp in enumerate(input_fields):
            inp_type = inp.get_attribute("type") or "unknown"
            inp_id = inp.get_attribute("id") or "no-id"
            inp_name = inp.get_attribute("name") or "no-name"
            inp_placeholder = inp.get_attribute("placeholder") or "no-placeholder"
            inp_class = inp.get_attribute("class") or "no-class"
            print(f"Input #{i}: type={inp_type}, id={inp_id}, name={inp_name}, placeholder={inp_placeholder}, class={inp_class}")
        
        # Based on the alert message, we need to handle the floating point numbers correctly
        # Try using JavaScript directly to set the coordinates
        try:
            print("Attempting to set coordinates using JavaScript...")
            
            # Try to find specific inputs for longitude and latitude
            longitude_input = None
            latitude_input = None
            
            # Method 1: Look by placeholder
            for inp in input_fields:
                placeholder = inp.get_attribute("placeholder") or ""
                if "longitude" in placeholder.lower():
                    longitude_input = inp
                elif "latitude" in placeholder.lower():
                    latitude_input = inp
            
            # Method 2: Look by input order (usually first two are longitude/latitude)
            if not longitude_input and len(input_fields) >= 1:
                longitude_input = input_fields[0]
            
            if not latitude_input and len(input_fields) >= 2:
                latitude_input = input_fields[1]
            
            # Try direct JavaScript injection first
            if longitude_input:
                print(f"Setting longitude to {longitude} using JavaScript")
                driver.execute_script(f"arguments[0].value = '{longitude}';", longitude_input)
                driver.execute_script("arguments[0].dispatchEvent(new Event('change'));", longitude_input)
                print("Longitude set successfully with JavaScript")
            
            if latitude_input:
                print(f"Setting latitude to {latitude} using JavaScript")
                driver.execute_script(f"arguments[0].value = '{latitude}';", latitude_input)
                driver.execute_script("arguments[0].dispatchEvent(new Event('change'));", latitude_input)
                print("Latitude set successfully with JavaScript")
                
            # Additional method: Try to set values through shadow DOM if applicable
            try:
                driver.execute_script(f"""
                    // Try to find inputs in any shadow DOM
                    function findInputsInShadowDOM(root, results) {{
                        if (!results) results = [];
                        if (!root) return results;
                        
                        // Check for shadow root
                        if (root.shadowRoot) {{
                            var shadowInputs = root.shadowRoot.querySelectorAll('input');
                            for (var i = 0; i < shadowInputs.length; i++) {{
                                results.push(shadowInputs[i]);
                            }}
                            
                            // Continue searching in shadow DOM children
                            var shadowChildren = root.shadowRoot.querySelectorAll('*');
                            for (var i = 0; i < shadowChildren.length; i++) {{
                                findInputsInShadowDOM(shadowChildren[i], results);
                            }}
                        }}
                        
                        // Search regular children
                        var children = root.querySelectorAll('*');
                        for (var i = 0; i < children.length; i++) {{
                            findInputsInShadowDOM(children[i], results);
                        }}
                        
                        return results;
                    }}
                    
                    var shadowInputs = findInputsInShadowDOM(document.documentElement);
                    console.log('Found ' + shadowInputs.length + ' inputs in shadow DOM');
                    
                    // Try to set the first two inputs as longitude and latitude
                    if (shadowInputs.length >= 1) {{
                        shadowInputs[0].value = '{longitude}';
                        shadowInputs[0].dispatchEvent(new Event('change'));
                        console.log('Set longitude in shadow DOM');
                    }}
                    
                    if (shadowInputs.length >= 2) {{
                        shadowInputs[1].value = '{latitude}';
                        shadowInputs[1].dispatchEvent(new Event('change'));
                        console.log('Set latitude in shadow DOM');
                    }}
                """)
                print("Attempted to set coordinates through shadow DOM")
            except Exception as e:
                print(f"Shadow DOM approach failed: {str(e)}")
            
            # Additional method: Try to interact with map element if present
            try:
                map_elements = driver.find_elements(By.XPATH, "//div[contains(@class, 'map')] | //div[contains(@class, 'leaflet')]")
                if map_elements:
                    print(f"Found {len(map_elements)} potential map elements")
                    # Try clicking on the map to set the coordinates
                    driver.execute_script("arguments[0].click();", map_elements[0])
                    print("Clicked on map element")
                    # After clicking, check if any input was populated
                    for inp in input_fields:
                        val = inp.get_attribute("value")
                        if val:
                            print(f"Input now has value: {val}")
            except Exception as e:
                print(f"Map interaction failed: {str(e)}")
            
        except Exception as e:
            print(f"Error setting coordinates with JavaScript: {str(e)}")
        
        # Take screenshot after attempting to enter coordinates
        coords_screenshot = "after_coordinates.png"
        driver.save_screenshot(coords_screenshot)
        print(f"Saved screenshot after setting coordinates to {coords_screenshot}")
        
        # Handle date inputs
        date_inputs = []
        for inp in input_fields:
            if longitude_input and inp != longitude_input and latitude_input and inp != latitude_input:
                date_inputs.append(inp)
        
        print(f"Found {len(date_inputs)} potential date input fields")
        
        # Process dates
        start_date_obj = datetime.strptime(start_date, "%d/%m/%Y")
        end_date_obj = datetime.strptime(end_date, "%d/%m/%Y")
        
        # Try multiple date formats for compatibility
        start_date_formats = {
            "MM/DD/YYYY": start_date_obj.strftime("%m/%d/%Y"),
            "YYYY-MM-DD": start_date_obj.strftime("%Y-%m-%d"),
            "DD-MM-YYYY": start_date_obj.strftime("%d-%m-%Y"),
            "DD/MM/YYYY": start_date_obj.strftime("%d/%m/%Y")
        }
        
        end_date_formats = {
            "MM/DD/YYYY": end_date_obj.strftime("%m/%d/%Y"),
            "YYYY-MM-DD": end_date_obj.strftime("%Y-%m-%d"),
            "DD-MM-YYYY": end_date_obj.strftime("%d-%m-%Y"),
            "DD/MM/YYYY": end_date_obj.strftime("%d/%m/%Y")
        }
        
        # Enter start date if we found date inputs
        if len(date_inputs) >= 1:
            start_date_input = date_inputs[0]
            print(f"Setting start date: {start_date}")
            
            # Try each format
            date_set = False
            for format_name, formatted_date in start_date_formats.items():
                if date_set:
                    break
                try:
                    print(f"Trying start date format: {format_name} = {formatted_date}")
                    driver.execute_script(f"arguments[0].value = '{formatted_date}';", start_date_input)
                    driver.execute_script("arguments[0].dispatchEvent(new Event('change'));", start_date_input)
                    print(f"Set start date with format {format_name}")
                    date_set = True
                except Exception as e:
                    print(f"Failed with format {format_name}: {str(e)}")
            
            # If all formats failed, try clicking to open date picker
            if not date_set:
                try:
                    start_date_input.click()
                    time.sleep(2)  # Wait for date picker to open
                    # Look for day element in date picker
                    day_elements = driver.find_elements(By.XPATH, 
                        f"//td[contains(@class, 'day') and text()='{start_date_obj.day}']")
                    if day_elements:
                        driver.execute_script("arguments[0].click();", day_elements[0])
                        print("Selected start date from date picker")
                except Exception as e:
                    print(f"Failed to use date picker for start date: {str(e)}")
        
        # Enter end date if we found enough date inputs
        if len(date_inputs) >= 2:
            end_date_input = date_inputs[1]
            print(f"Setting end date: {end_date}")
            
            # Try each format
            date_set = False
            for format_name, formatted_date in end_date_formats.items():
                if date_set:
                    break
                try:
                    print(f"Trying end date format: {format_name} = {formatted_date}")
                    driver.execute_script(f"arguments[0].value = '{formatted_date}';", end_date_input)
                    driver.execute_script("arguments[0].dispatchEvent(new Event('change'));", end_date_input)
                    print(f"Set end date with format {format_name}")
                    date_set = True
                except Exception as e:
                    print(f"Failed with format {format_name}: {str(e)}")
            
            # If all formats failed, try clicking to open date picker
            if not date_set:
                try:
                    end_date_input.click()
                    time.sleep(2)  # Wait for date picker to open
                    # Look for day element in date picker
                    day_elements = driver.find_elements(By.XPATH, 
                        f"//td[contains(@class, 'day') and text()='{end_date_obj.day}']")
                    if day_elements:
                        driver.execute_script("arguments[0].click();", day_elements[0])
                        print("Selected end date from date picker")
                except Exception as e:
                    print(f"Failed to use date picker for end date: {str(e)}")
        
        # Take screenshot after entering dates
        dates_screenshot = "after_dates.png"
        driver.save_screenshot(dates_screenshot)
        print(f"Saved screenshot after entering dates to {dates_screenshot}")
        
        # Find and click the submit button
        print("Looking for submit button...")
        submit_button = None
        
        # Method 1: Look by button text
        try:
            submit_buttons = driver.find_elements(By.XPATH, "//button[contains(translate(text(), 'SUBMIT', 'submit'), 'submit')]")
            if submit_buttons:
                submit_button = submit_buttons[0]
                print("Found submit button by text")
        except Exception as e:
            print(f"Error finding submit button by text: {str(e)}")
        
        # Method 2: Look by common button classes
        if not submit_button:
            try:
                submit_buttons = driver.find_elements(By.CSS_SELECTOR, ".submit, .btn-submit, .submitButton")
                if submit_buttons:
                    submit_button = submit_buttons[0]
                    print("Found submit button by class")
            except Exception as e:
                print(f"Error finding submit button by class: {str(e)}")
        
        # Method 3: Look for any button
        if not submit_button:
            try:
                buttons = driver.find_elements(By.TAG_NAME, "button")
                if buttons:
                    submit_button = buttons[0]
                    print("Using first button as submit button")
            except Exception as e:
                print(f"Error finding buttons: {str(e)}")
        
        # Click the submit button if found
        if submit_button:
            try:
                print("Clicking submit button...")
                driver.execute_script("arguments[0].scrollIntoView(true);", submit_button)
                time.sleep(1)  # Give time to scroll into view
                
                # Check and handle any alerts before clicking
                try:
                    alert = Alert(driver)
                    alert_text = alert.text
                    print(f"Alert present before clicking: {alert_text}")
                    alert.accept()
                except:
                    pass  # No alert present
                
                # Click the button
                driver.execute_script("arguments[0].click();", submit_button)
                print("Clicked submit button using JavaScript")
                
                # Handle any alerts that pop up after clicking
                try:
                    time.sleep(2)  # Wait for alert to appear
                    alert = Alert(driver)
                    alert_text = alert.text
                    print(f"Alert appeared after clicking: {alert_text}")
                    alert.accept()
                    
                    # If the alert complained about coordinates, try to fix and resubmit
                    if "latitude" in alert_text.lower() or "longitude" in alert_text.lower() or "point" in alert_text.lower():
                        print("Alert mentioned coordinates issue. Trying alternative approach...")
                        
                        # Try using a different way to input coordinates
                        try:
                            print("Searching for coordinate inputs again...")
                            # Refresh page and try again
                            driver.refresh()
                            time.sleep(5)
                            
                            # Try to click Time Series again
                            time_series_elements = driver.find_elements(By.XPATH, "//*[contains(text(), 'Time Series')]")
                            if time_series_elements:
                                driver.execute_script("arguments[0].click();", time_series_elements[0])
                                print("Clicked Time Series again after refresh")
                                time.sleep(2)
                            
                            # Try using the map interface if available
                            map_elements = driver.find_elements(By.TAG_NAME, "canvas")
                            if map_elements:
                                print("Found canvas element, trying to click on map")
                                ActionChains(driver).move_to_element(map_elements[0]).click().perform()
                                print("Clicked on map canvas")
                            
                            # Re-get the input fields after refresh
                            input_fields = driver.find_elements(By.TAG_NAME, "input")
                            
                            # Try sending the values directly with ActionChains
                            if len(input_fields) >= 2:
                                print("Trying ActionChains to send values to first two inputs")
                                ActionChains(driver).click(input_fields[0]).send_keys(Keys.CONTROL, "a").send_keys(Keys.DELETE).send_keys(longitude).perform()
                                time.sleep(1)
                                ActionChains(driver).click(input_fields[1]).send_keys(Keys.CONTROL, "a").send_keys(Keys.DELETE).send_keys(latitude).perform()
                                time.sleep(1)
                                print("Used ActionChains to set coordinates")
                                
                                # Re-submit
                                submit_buttons = driver.find_elements(By.XPATH, "//button[contains(translate(text(), 'SUBMIT', 'submit'), 'submit')]")
                                if submit_buttons:
                                    driver.execute_script("arguments[0].click();", submit_buttons[0])
                                    print("Re-clicked submit after fixing coordinates")
                            
                        except Exception as e:
                            print(f"Alternative coordinates approach failed: {str(e)}")
                except:
                    pass  # No alert present
                
            except Exception as e:
                print(f"Error clicking submit button with JavaScript: {str(e)}")
                try:
                    ActionChains(driver).move_to_element(submit_button).click().perform()
                    print("Clicked submit button with ActionChains")
                    
                    # Handle any alerts after clicking
                    try:
                        time.sleep(2)  # Wait for alert to appear
                        alert = Alert(driver)
                        print(f"Alert after ActionChains click: {alert.text}")
                        alert.accept()
                    except:
                        pass  # No alert present
                    
                except Exception as e2:
                    print(f"Error clicking submit button with ActionChains: {str(e2)}")
        else:
            print("Could not find a submit button")
        
        # Take screenshot after clicking submit
        submit_screenshot = "after_submit.png"
        driver.save_screenshot(submit_screenshot)
        print(f"Saved screenshot after submit to {submit_screenshot}")
        
        # Wait for results to load
        print("Waiting for results to load...")
        time.sleep(20)  # Extended wait time for results
        
        # Take final screenshot 
        final_screenshot = "final_results.png"
        driver.save_screenshot(final_screenshot)
        print(f"Saved final screenshot to {final_screenshot}")
        
        # Extract data from the page
        print("Extracting data...")
        data = {
            "screenshots": {
                "initial_page": initial_screenshot,
                "after_time_series": time_series_screenshot,
                "form_view": form_screenshot,
                "after_coordinates": coords_screenshot,
                "after_dates": dates_screenshot,
                "after_submit": submit_screenshot,
                "final_results": final_screenshot
            }
        }
        
        # Try to extract actual data
        try:
            # Look for tables
            tables = driver.find_elements(By.TAG_NAME, "table")
            if tables:
                print(f"Found {len(tables)} tables")
                all_table_data = []
                
                # Process each table
                for table_idx, table in enumerate(tables):
                    table_data = []
                    headers = []
                    
                    try:
                        rows = table.find_elements(By.TAG_NAME, "tr")
                        for i, row in enumerate(rows):
                            cells = row.find_elements(By.TAG_NAME, "td")
                            if not cells:  # Might be header row with th
                                cells = row.find_elements(By.TAG_NAME, "th")
                            
                            row_data = [cell.text for cell in cells]
                            
                            if i == 0:  # Assuming first row is headers
                                headers = row_data
                            else:
                                if row_data:  # Only add non-empty rows
                                    table_data.append(row_data)
                        
                        # Only add tables with actual data
                        if headers or table_data:
                            all_table_data.append({
                                "table_index": table_idx,
                                "headers": headers,
                                "data": table_data
                            })
                    except Exception as e:
                        print(f"Error processing table {table_idx}: {str(e)}")
                
                # Use the first table with data as the primary table
                if all_table_data:
                    data["all_tables"] = all_table_data
                    # Find the first table with actual data
                    for table_info in all_table_data:
                        if table_info["data"]:
                            data["table"] = table_info
                            break
                    if "table" not in data and all_table_data:
                        data["table"] = all_table_data[0]  # Just use the first table if none have data
            
            # Look for chart/graph elements
            charts = driver.find_elements(By.TAG_NAME, "canvas")
            charts.extend(driver.find_elements(By.TAG_NAME, "svg"))
            if charts:
                print(f"Found {len(charts)} chart/graph elements")
                data["chart_elements"] = len(charts)
            
            # Look for any numeric content that might be soil wetness data
            number_elements = driver.find_elements(By.XPATH, "//*[contains(text(), '.')]")
            potential_data = []
            for elem in number_elements:
                text = elem.text
                if text and any(c.isdigit() for c in text):
                    try:
                        # Check if it's a number
                        float(text.replace(',', ''))
                        potential_data.append(text)
                    except ValueError:
                        # If multiple numbers in text, extract them
                        import re
                        numbers = re.findall(r"[-+]?\d*\.\d+|\d+", text)
                        if numbers:
                            potential_data.extend(numbers)
            
            if potential_data:
                print(f"Found {len(potential_data)} potential numeric data points")
                data["numeric_data"] = potential_data[:30]  # Limit to first 30 values
            
            # Capture page source in case we need to analyze it further
            data["page_source"] = driver.page_source
            
        except Exception as e:
            print(f"Error during data extraction: {str(e)}")
            data["error_during_extraction"] = str(e)
        
        print("Data extraction complete!")
        return data
        
    except UnexpectedAlertPresentException as alert_error:
        print(f"Alert interrupted execution: {str(alert_error)}")
        try:
            # Try to get the alert text
            alert = Alert(driver)
            alert_text = alert.text
            print(f"Alert text: {alert_text}")
            alert.accept()
            
            # Take a screenshot
            alert_screenshot = "alert_state.png"
            driver.save_screenshot(alert_screenshot)
            print(f"Saved alert state screenshot to {alert_screenshot}")
            
            return {
                "error": f"Alert interrupted execution: {alert_text}",
                "error_screenshot": alert_screenshot,
                "page_source": driver.page_source
            }
        except:
            # If we can't get the alert text
            error_screenshot = "error_state.png"
            driver.save_screenshot(error_screenshot)
            print(f"Saved error state screenshot to {error_screenshot}")
            return {
                "error": str(alert_error),
                "error_screenshot": error_screenshot,
                "page_source": driver.page_source
            }
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        # Try to capture a screenshot of the error state
        try:
            error_screenshot = "error_state.png"
            driver.save_screenshot(error_screenshot)
            print(f"Saved error state screenshot to {error_screenshot}")
            return {
                "error": str(e),
                "error_screenshot": error_screenshot,
                "page_source": driver.page_source
            }
        except:
            return {"error": str(e)}
    
    finally:
        # Close the browser
        print("Closing WebDriver...")
        try:
            driver.quit()
        except Exception as e:
            print(f"Error closing browser: {str(e)}")

def save_data_to_files(data, longitude, latitude):
    """Save the scraped data to files."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    folder_name = f"soil_wetness_data_{longitude}_{latitude}_{timestamp}"
    
    try:
        # Create directory if it doesn't exist
        if not os.path.exists(folder_name):
            os.makedirs(folder_name)
        
        # Copy screenshots to folder (but don't delete originals)
        if "screenshots" in data:
            for name, path in data["screenshots"].items():
                if os.path.exists(path):
                    new_path = os.path.join(folder_name, f"{name}.png")
                    import shutil
                    shutil.copy(path, new_path)
                    print(f"Copied screenshot {path} to {new_path}")
        
        # Copy error screenshot if present (but don't delete original)
        if "error_screenshot" in data and os.path.exists(data["error_screenshot"]):
            import shutil
            error_path = os.path.join(folder_name, "error.png")
            shutil.copy(data["error_screenshot"], error_path)
            print(f"Copied error screenshot to {error_path}")
        
        # Save raw data as JSON
        with open(os.path.join(folder_name, "raw_data.json"), "w") as f:
            # Create a copy of data without page_source to make the JSON more readable
            data_copy = {k: v for k, v in data.items() if k != "page_source"}
            json.dump(data_copy, f, indent=4)
        
        # Save page source separately
        if "page_source" in data:
            with open(os.path.join(folder_name, "page_source.html"), "w", encoding="utf-8") as f:
                f.write(data["page_source"])
        
        # If there's table data, save as CSV
        if "table" in data and data["table"]["headers"] and data["table"]["data"]:
            try:
                df = pd.DataFrame(data["table"]["data"], columns=data["table"]["headers"])
                df.to_csv(os.path.join(folder_name, "table_data.csv"), index=False)
                print(f"Table data saved to {folder_name}/table_data.csv")
            except Exception as e:
                print(f"Error saving table data to CSV: {str(e)}")
                # Try a more robust approach
                try:
                    # If headers and data don't match, create a simple DataFrame
                    print("Trying alternative CSV saving approach...")
                    with open(os.path.join(folder_name, "table_data.txt"), "w") as f:
                        if data["table"]["headers"]:
                            f.write(",".join(data["table"]["headers"]) + "\n")
                        for row in data["table"]["data"]:
                            f.write(",".join(str(cell) for cell in row) + "\n")
                    print(f"Table data saved to {folder_name}/table_data.txt")
                except Exception as e2:
                    print(f"Alternative approach also failed: {str(e2)}")
        
        # If we found numeric data, save it
        if "numeric_data" in data and data["numeric_data"]:
            with open(os.path.join(folder_name, "numeric_data.txt"), "w") as f:
                f.write("\n".join(data["numeric_data"]))
        
        print(f"All data saved to folder: {folder_name}")
        return folder_name
    
    except Exception as e:
        print(f"Error saving data: {str(e)}")
        return None

def main():
    print("\n" + "="*50)
    print("Soil Wetness Index Data Scraper for MOSDAC")
    print("="*50 + "\n")
    
    # Get user inputs with validation to ensure they're floating point numbers
    while True:
        longitude = input("Enter longitude (e.g., 77.88): ")
        try:
            float(longitude)
            break
        except ValueError:
            print("Please enter a valid floating point number for longitude.")
    
    while True:
        latitude = input("Enter latitude (e.g., 23.47): ")
        try:
            float(latitude)
            break
        except ValueError:
            print("Please enter a valid floating point number for latitude.")
    
    # Date inputs with validation
    while True:
        start_date = input("Enter start date (DD/MM/YYYY): ")
        try:
            datetime.strptime(start_date, "%d/%m/%Y")
            break
        except ValueError:
            print("Invalid date format. Please use DD/MM/YYYY.")
    
    while True:
        end_date = input("Enter end date (DD/MM/YYYY): ")
        try:
            datetime.strptime(end_date, "%d/%m/%Y")
            break
        except ValueError:
            print("Invalid date format. Please use DD/MM/YYYY.")
    
    print("\nStarting web scraping process...")
    print("-"*40)
    
    # Scrape the data
    data = scrape_soil_wetness_data(longitude, latitude, start_date, end_date)
    
    # Process and display the data
    if "error" in data and not any(k != "error" and k != "error_screenshot" and k != "page_source" for k in data.keys()):
        print(f"\nFailed to scrape data: {data['error']}")
        if "error_screenshot" in data:
            print(f"Error state screenshot saved to: {data['error_screenshot']}")
    else:
        print("\nData scraping complete!")
        
        # Save the data
        try:
            output_folder = save_data_to_files(data, longitude, latitude)
            
            # Display a summary of what we found
            print("\nSummary of scraped data:")
            print("-"*40)
            
            if "screenshots" in data:
                print(f"• Screenshots: Captured {len(data['screenshots'])} screenshots of the process")
            
            if "all_tables" in data:
                print(f"• Tables: Found {len(data['all_tables'])} tables on the page")
                
            if "table" in data:
                headers_count = len(data["table"]["headers"]) if data["table"]["headers"] else 0
                rows_count = len(data["table"]["data"]) if data["table"]["data"] else 0
                print(f"• Main table data: Found with {headers_count} columns and {rows_count} rows")
            
            if "chart_elements" in data:
                print(f"• Chart elements: Detected {data['chart_elements']} chart/graph elements on the page")
            
            if "numeric_data" in data:
                print(f"• Numeric data: Found {len(data['numeric_data'])} potential soil wetness values")
            
            if "error_during_extraction" in data:
                print(f"• Note: Some errors occurred during data extraction: {data['error_during_extraction']}")
            
            print(f"\nAll data has been saved to folder: {output_folder}")
            print("\nProcess completed successfully!")
            print("Check the screenshots in the output folder to see the actual web page state during scraping.")
        except Exception as e:
            print(f"\nError during data processing: {str(e)}")
            print("The scraping was successful, but there was an error processing the results.")
            print("Check the screenshots to see what data was found.")

if __name__ == "__main__":
    main() 