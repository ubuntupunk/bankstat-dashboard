import streamlit as st
from datetime import datetime
from utils import debug_write

def render_upload_tab(pdf_processor, processor, db_connection):
    st.header("📁 Upload Bank Statement")

    # File upload section
    st.markdown('<div class="upload-area">', unsafe_allow_html=True)
    uploaded_file = st.file_uploader(
        "Drop your PDF bank statement here",
        type=['pdf'],
        help="Upload a PDF bank statement to process and analyze",
        key="pdf_uploader"
    )
    st.markdown('</div>', unsafe_allow_html=True)

    if uploaded_file is not None:
        col1, col2 = st.columns([2, 1])

        with col1:
            st.info(f"📄 File: {uploaded_file.name}")
            st.info(f"📏 Size: {uploaded_file.size:,} bytes")

        with col2:
            # Initialize session state for processed data
            if 'processed_json' not in st.session_state:
                st.session_state.processed_json = None

            if st.button("🚀 Process PDF", type="primary", key="process_pdf_button"):
                with st.spinner("Processing PDF... This may take a moment..."):
                    try:
                        # Process the PDF
                        json_data = pdf_processor.process_pdf(uploaded_file)
                        if json_data:
                            st.success("✅ PDF processed successfully!")
                            st.session_state.processed_json = json_data

                            # Display extracted data
                            st.subheader("📊 Extracted Data Preview")
                            df = processor.extract_tables_to_dataframe(json_data)
                            if not df.empty:
                                st.dataframe(df.head(10), use_container_width=True)
                            else:
                                st.warning("No tabular data extracted from PDF")
                        else:
                            st.error("❌ Failed to process PDF")
                            st.session_state.processed_json = None
                    except Exception as e:
                        st.error(f"Error processing PDF: {str(e)}")
                        st.session_state.processed_json = None
                        debug_write("🔧 Debug info:")
                        debug_write(f"- Error type: {type(e).__name__}")
                        debug_write(f"- Error message: {str(e)}")

            # Save to Database button (only shown if PDF was processed successfully)
            if st.session_state.processed_json:
                with st.status("Database Upload Status", expanded=True) as status:
                    if st.button("💾 Save to Database", key="save_to_db_button"):
                        try:
                            status.write("📁 Saving to local file...")
                            if processor.save_bank_statement(st.session_state.processed_json):
                                status.write("✅ Saved to local file!")
                            else:
                                status.write("❌ Failed to save local file!")
                                st.error("Failed to save to local file")
                                return

                            status.write("🛢️ Starting MongoDB upload process...")
                            status.write(f"📊 JSON data keys: {list(st.session_state.processed_json.keys())}")
                            status.write(f"📄 Filename: {st.session_state.processed_json.get('filename', 'Unknown')}")

                            # Test database connection
                            status.write("🔌 Testing MongoDB connection...")
                            conn_success, conn_message = db_connection.test_connection()
                            if not conn_success:
                                raise Exception(f"Database connection failed: {conn_message}")

                            status.write(f"✅ {conn_message}")

                            # Add metadata
                            st.session_state.processed_json['uploaded_at'] = datetime.now().isoformat()
                            st.session_state.processed_json['processed_by'] = 'streamlit_app'

                            # Insert document
                            status.write("📝 Inserting document...")
                            inserted_id = db_connection.insert_document(st.session_state.processed_json)
                            status.write(f"✅ Success! Document ID: {inserted_id}")

                            # Verify insertion
                            doc_count = db_connection.count_documents()
                            status.write(f"📊 Total documents in collection: {doc_count}")

                            status.update(label="✅ Data uploaded to MongoDB successfully!", state="complete")
                            st.success("✅ Data uploaded to MongoDB successfully!")
                            st.info("💡 Data is now in database. You can view it in the Dashboard tab.")
                        except Exception as e:
                            status.write(f"❌ MongoDB upload failed: {str(e)}")
                            status.update(label=f"❌ Upload Failed: {str(e)}", state="error")
                            st.error(f"❌ MongoDB upload failed: {str(e)}")
                            debug_write("🔧 Debug info:")
                            debug_write(f"- Error type: {type(e).__name__}")
                            debug_write(f"- Error message: {str(e)}")
                            try:
                                test_collection = db_connection.get_collection()
                                if test_collection:
                                    debug_write(f"- Collection name: {test_collection.name}")
                                    debug_write(f"- Database name: {test_collection.database.name}")
                                else:
                                    debug_write("- Collection connection returned None")
                            except Exception as debug_e:
                                debug_write(f"- Additional debug error: {str(debug_e)}")
            else:
                st.info("Please process the PDF first before saving to database.")