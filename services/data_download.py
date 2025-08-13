

import cdsapi
import ddsapi
import logging
from qgis.core import QgsTask, QgsMessageLog, QgsMeshLayer, QgsLayerTreeLayer, QgsApplication, Qgis, QgsRasterLayer, QgsProject
from datetime import datetime
import zipfile
import os
from osgeo import gdal
from ..module.display_error_message import DisplayErrorMessage
import sys

class DownloadServices:
    base_dir = os.path.expanduser('~')  # Gets the user's home directory
    target_file_download = os.path.join(base_dir, 'Documents/')
        

    class DownloadCDSTask(QgsTask):
        def __init__(self, description, selected_items, widget_creator):
            super().__init__(description, QgsTask.CanCancel)
            self.target_file = DownloadServices.target_file_download
            self.widget_creator = widget_creator
            self.selected_items = selected_items
            
        
        def run(self):
            QgsMessageLog.logMessage("Simple task is running...", level=Qgis.Info)

            try:
                c = cdsapi.Client()
                QgsMessageLog.logMessage("CDS Client initialized.", level=Qgis.Info)

                dataset = self.selected_items.get('dataset')
                items = self.selected_items.get('items')

                # Getting the current date and time in the desired format
                current_datetime = datetime.now().strftime('%Y%m%d_%H%M%S')

                download_format = items.get('download_format', '').lower()
                data_format = items.get('data_format', '').lower()


                if download_format == 'zip':
                        path_file = self.target_file + f"{dataset}_{current_datetime}.zip"
                elif not download_format and data_format in ['netcdf', 'grib']:
                        path_file = self.target_file + f"{dataset}_{current_datetime}.{data_format}"
                elif download_format == 'unarchived':
                    if data_format in ['netcdf', 'grib']:
                        path_file = self.target_file + f"{dataset}_{current_datetime}.{data_format}"
                    else:
                        raise ValueError(f"Unsupported or missing data format for unarchived download: {data_format}")
                else:
                    path_file = self.target_file + f"{dataset}_{current_datetime}" #raise ValueError(f"Unsupported download format: {download_format}")

                # Validate input
                if not isinstance(items, dict):
                    raise ValueError("Expected 'items' to be a dictionary, but got: {}".format(type(items)))

                print("SENT TO:", dataset, items, path_file)

                c.retrieve(dataset, items, path_file)
                QgsMessageLog.logMessage("Data retrieved successfully.", level=Qgis.Info)

                # Check if the file is a ZIP archive
                if zipfile.is_zipfile(path_file):
                    QgsMessageLog.logMessage(f"Downloaded file is a ZIP archive: {path_file}", level=Qgis.Info)
                    print("Downloaded file is a ZIP")
                    # Extract the ZIP file
                    with zipfile.ZipFile(path_file, 'r') as zip_ref:
                        extracted_files = zip_ref.namelist()
                        zip_ref.extractall(self.target_file)
                        QgsMessageLog.logMessage("ZIP file extracted successfully.", level=Qgis.Info)

                    # Rename extracted files
                    for idx, file_name in enumerate(extracted_files, start=1):
                        original_path = os.path.join(self.target_file, file_name)
                        if os.path.isfile(original_path):
                            file_ext = os.path.splitext(file_name)[1]  # Extract file extension
                            new_name = f"{dataset}_{current_datetime}_{idx}{file_ext}"
                            new_path = os.path.join(self.target_file, new_name)
                            os.rename(original_path, new_path)
                            QgsMessageLog.logMessage(f"Renamed file {original_path} to {new_path}", level=Qgis.Info)

                            # Load the file into QGIS if it is a NetCDF (.nc) or GRIB file
                            if new_path.endswith(('.nc', '.grib')):
                                DownloadServices.load_multiband_file_to_qgis(new_path)

                else:
                    QgsMessageLog.logMessage("Downloaded file is not a ZIP archive.", level=Qgis.Info)

                
                # Load the file into QGIS if it is a NetCDF (.nc) file
                if path_file.endswith(('.nc', '.grib')) or self.detect_file_type(path_file):
                    print("Loading file to QGIS")
                    DownloadServices.load_multiband_file_to_qgis(path_file)
                else:
                    print("Unsupported file format")

                return True  # Task successful
             
            except Exception as e:
                #DownloadServices.logger.error("TypeError: %s", e)
                print("ERROR TYPE", "TypeError: %s", e)
                QgsMessageLog.logMessage(f"Failed to retrieve data: {e}", level=Qgis.Critical)
                return False  # Task failed
            

        def detect_file_type(self, path_file):
            try:
                with open(path_file, 'rb') as f:
                    header = f.read(4)
                    # Check for GRIB magic number
                    if header.startswith(b'GRIB'):
                        return True
                    # Check for NetCDF magic number
                    if header.startswith(b'CDF'):
                        return True
                return False
            except Exception as e:
                print(f"Error reading file: {e}")
                return False


        def finished(self, result):
            if result:
                QgsMessageLog.logMessage("CDS download completed successfully.", level=Qgis.Info)
            else:
                error_message = "CDS download failed. Please check your input and try again."
                QgsMessageLog.logMessage("CDS download failed.", level=Qgis.Warning)
                #error_display = DisplayErrorMessage(self.widget_creator.verticalLayout, parent=self.widget_creator.dialog)
                #error_display.display_error_message(error_message, True)
                # Use the existing error_display instance
                if self.widget_creator and self.widget_creator.error_display:
                    self.widget_creator.error_display.display_error_message(error_message, True)
                else:
                    QgsMessageLog.logMessage("Error display instance is missing. Cannot show error message.", level=Qgis.Critical)


    class DownloadCMCCTask(QgsTask):
        def __init__(self, description, selected_items):
            super().__init__(description, QgsTask.CanCancel)
            self.target_file = DownloadServices.target_file_download
            self.selected_items = selected_items
        
        
        def run(self):
            QgsMessageLog.logMessage("Simple task is running...", level=Qgis.Info)

            try:
                c = ddsapi.Client()
                QgsMessageLog.logMessage("CMCC Client initialized.", level=Qgis.Info)
                # Check if DDS API's logger is correctly configured
                '''dds_logger = logging.getLogger('ddsapi')

                for handler in list(dds_logger.handlers):
                    dds_logger.removeHandler(handler)
                
                if not dds_logger.handlers:
                    # Adding a handler if it's missing
                    handler = logging.StreamHandler()
                    handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
                    dds_logger.addHandler(handler)
                    dds_logger.setLevel(logging.INFO)'''

                file_id = self.selected_items.get('id')
                current_datetime = datetime.now().strftime('%Y%m%d_%H%M%S')
                path_file = self.target_file +f"{file_id}_{current_datetime}.nc"

                id_dataset = self.selected_items.get('id')
                product = self.selected_items.get('product')
                items = self.selected_items.get('items')

                print("retrieving", id_dataset, product, items, path_file)
                #response = self.data_service.postEstimateData(items)
                # Start the data retrieval
                #if response and response.get("status") == "OK":
                c.retrieve(id_dataset, product, items, path_file)
                DownloadServices.load_multiband_file_to_qgis(path_file)
                return True
            
            except TypeError as te:
                #DownloadServices.logger.error("TypeError: %s", te)
                print("ERROR TYPE", "TypeError: %s", te)
            except Exception as e:
                #DownloadServices.logger.error("Failed to download CMCC data: %s", e)
                print("Failed to download CMCC data: %s", e)

            return False


        def finished(self, result):
            if result:
                QgsMessageLog.logMessage("CMCC download completed successfully.", level=Qgis.Info)
            else:
                QgsMessageLog.logMessage("CMCC download failed.", level=Qgis.Warning)


    @staticmethod
    def load_multiband_file_to_qgis(file_path):
        """Load all bands from a multi-layer NetCDF or GRIB file into QGIS."""
        print("start to add the netCDF to QGIS", file_path)
        #DownloadServices.info_layer(file_path)
        QgsMessageLog.logMessage(f"Inspecting file: {file_path}", level=Qgis.Info)

        root = QgsProject.instance().layerTreeRoot()

        # Load as a raster layer (GDAL)
        dataset = gdal.Open(file_path)
        raster_layer = None
        if dataset:
            # Check for subdatasets
            subdatasets = dataset.GetSubDatasets()
            if subdatasets:
                QgsMessageLog.logMessage(f"Found {len(subdatasets)} subdatasets in the file.", level=Qgis.Info)
                for subdataset in subdatasets:
                    subdataset_name = subdataset[0]
                    subdataset_description = subdataset[1]

                    raster_layer_name = f"{os.path.basename(file_path)} - {subdataset_description}"
                    raster_layer = QgsRasterLayer(subdataset_name, raster_layer_name, "gdal")

                    if raster_layer.isValid():
                        QgsProject.instance().addMapLayer(raster_layer)
                        QgsMessageLog.logMessage(f"Subdataset '{raster_layer_name}' loaded successfully.", level=Qgis.Info)
                    else:
                        QgsMessageLog.logMessage(f"Failed to load subdataset: {subdataset_description}", level=Qgis.Warning)
            else:
                QgsMessageLog.logMessage(f"No subdatasets found in file '{file_path}'. Attempting to load as a single raster layer.", level=Qgis.Info)

                # Load as a single raster layer if no subdatasets
                raster_layer_name = f"{os.path.basename(file_path)} (Raster)"
                raster_layer = QgsRasterLayer(file_path, raster_layer_name, "gdal")

                if raster_layer.isValid():
                    QgsProject.instance().addMapLayer(raster_layer)
                    QgsMessageLog.logMessage(f"Raster layer '{raster_layer_name}' loaded successfully.", level=Qgis.Info)
                else:
                    QgsMessageLog.logMessage(f"Failed to load file '{file_path}' as a raster layer.", level=Qgis.Critical)

        # Close GDAL dataset
        dataset = None

        # Load the file as a mesh layer
        mesh_layer = QgsMeshLayer(file_path, f"{os.path.basename(file_path)} (Mesh)", "mdal")

        if mesh_layer.isValid():
            QgsProject.instance().addMapLayer(mesh_layer)  # Add mesh without auto-inserting in canvas
            mesh_node = root.findLayer(mesh_layer.id())
            if mesh_node:
                # Remove the layer if it already exists
                root.removeLayer(mesh_layer)

                # Insert the layer at the top
                root.insertChildNode(0, mesh_node)

            QgsMessageLog.logMessage(f"Mesh layer '{os.path.basename(file_path)}' loaded successfully.", level=Qgis.Info)
        else:
            QgsMessageLog.logMessage(f"File '{file_path}' is not a valid mesh layer.", level=Qgis.Warning)



    def start_cds_download(selected_items, widget_creator):
        QgsMessageLog.logMessage("Initiating CDS download task...", level=Qgis.Info)
        task = DownloadServices.DownloadCDSTask("Downloading CDS data", selected_items, widget_creator)
        QgsApplication.taskManager().addTask(task)
        QgsMessageLog.logMessage("Task added to manager.", level=Qgis.Info)
        return task

    def start_cmcc_download(selected_items):
        QgsMessageLog.logMessage("Initiating CMCC download task...", level=Qgis.Info)
        task = DownloadServices.DownloadCMCCTask("Downloading CMCC data", selected_items)
        QgsApplication.taskManager().addTask(task)
        QgsMessageLog.logMessage("Task added to manager.", level=Qgis.Info)
        return task




#Check info layers
    @staticmethod
    def info_layer(file_path):
        dataset = gdal.Open(file_path)
        if dataset is None:
            print("Failed to open the dataset.")
        else:
            print("Driver: ", dataset.GetDriver().LongName)
            print("Size: ", dataset.RasterXSize, "x", dataset.RasterYSize)
            print("Number of Bands: ", dataset.RasterCount)

            # Check for subdatasets
            subdatasets = dataset.GetSubDatasets()
            if subdatasets:
                print("Subdatasets:")
                for idx, subdataset in enumerate(subdatasets, 1):
                    print(f"  Subdataset {idx}: {subdataset}")
            else:
                print("No subdatasets found.")

            # Print metadata of the dataset
            metadata = dataset.GetMetadata()
            if metadata:
                print("Metadata:")
                for key, value in metadata.items():
                    print(f"  {key}: {value}")

            # Check the bands if there are no subdatasets
            if not subdatasets:
                print("Bands:")
                for band_idx in range(1, dataset.RasterCount + 1):
                    band = dataset.GetRasterBand(band_idx)
                    print(f"Band {band_idx}:")
                    print(f"Data Type: {gdal.GetDataTypeName(band.DataType)}")
                    print(f"Size: {band.XSize} x {band.YSize}")
                    print(f"Description: {band.GetDescription()}")
                    print(f"Metadata: {band.GetMetadata()}")



