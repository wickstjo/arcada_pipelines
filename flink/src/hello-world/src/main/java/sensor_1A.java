/**
 * Autogenerated by Avro
 * 
 * DO NOT EDIT DIRECTLY
 */
package schemas.surface_data;  
@SuppressWarnings("all")
@org.apache.avro.specific.AvroGenerated
public class sensor_1A extends org.apache.avro.specific.SpecificRecordBase implements org.apache.avro.specific.SpecificRecord {
  private static final long serialVersionUID = 5062825515826472710L;
  public static final org.apache.avro.Schema SCHEMA$ = new org.apache.avro.Schema.Parser().parse("{\"type\":\"record\",\"name\":\"sensor_1A\",\"namespace\":\"schemas.surface_data\",\"fields\":[{\"name\":\"timestamp\",\"type\":\"string\"},{\"name\":\"serial_number\",\"type\":\"string\"},{\"name\":\"datapoints\",\"type\":{\"type\":\"array\",\"items\":\"double\"}}]}");
  public static org.apache.avro.Schema getClassSchema() { return SCHEMA$; }
  @Deprecated public java.lang.CharSequence timestamp;
  @Deprecated public java.lang.CharSequence serial_number;
  @Deprecated public java.util.List<java.lang.Double> datapoints;

  /**
   * Default constructor.  Note that this does not initialize fields
   * to their default values from the schema.  If that is desired then
   * one should use <code>newBuilder()</code>. 
   */
  public sensor_1A() {}

  /**
   * All-args constructor.
   */
  public sensor_1A(java.lang.CharSequence timestamp, java.lang.CharSequence serial_number, java.util.List<java.lang.Double> datapoints) {
    this.timestamp = timestamp;
    this.serial_number = serial_number;
    this.datapoints = datapoints;
  }

  public org.apache.avro.Schema getSchema() { return SCHEMA$; }
  // Used by DatumWriter.  Applications should not call. 
  public java.lang.Object get(int field$) {
    switch (field$) {
    case 0: return timestamp;
    case 1: return serial_number;
    case 2: return datapoints;
    default: throw new org.apache.avro.AvroRuntimeException("Bad index");
    }
  }
  // Used by DatumReader.  Applications should not call. 
  @SuppressWarnings(value="unchecked")
  public void put(int field$, java.lang.Object value$) {
    switch (field$) {
    case 0: timestamp = (java.lang.CharSequence)value$; break;
    case 1: serial_number = (java.lang.CharSequence)value$; break;
    case 2: datapoints = (java.util.List<java.lang.Double>)value$; break;
    default: throw new org.apache.avro.AvroRuntimeException("Bad index");
    }
  }

  /**
   * Gets the value of the 'timestamp' field.
   */
  public java.lang.CharSequence getTimestamp() {
    return timestamp;
  }

  /**
   * Sets the value of the 'timestamp' field.
   * @param value the value to set.
   */
  public void setTimestamp(java.lang.CharSequence value) {
    this.timestamp = value;
  }

  /**
   * Gets the value of the 'serial_number' field.
   */
  public java.lang.CharSequence getSerialNumber() {
    return serial_number;
  }

  /**
   * Sets the value of the 'serial_number' field.
   * @param value the value to set.
   */
  public void setSerialNumber(java.lang.CharSequence value) {
    this.serial_number = value;
  }

  /**
   * Gets the value of the 'datapoints' field.
   */
  public java.util.List<java.lang.Double> getDatapoints() {
    return datapoints;
  }

  /**
   * Sets the value of the 'datapoints' field.
   * @param value the value to set.
   */
  public void setDatapoints(java.util.List<java.lang.Double> value) {
    this.datapoints = value;
  }

  /**
   * Creates a new sensor_1A RecordBuilder.
   * @return A new sensor_1A RecordBuilder
   */
  public static schemas.surface_data.sensor_1A.Builder newBuilder() {
    return new schemas.surface_data.sensor_1A.Builder();
  }
  
  /**
   * Creates a new sensor_1A RecordBuilder by copying an existing Builder.
   * @param other The existing builder to copy.
   * @return A new sensor_1A RecordBuilder
   */
  public static schemas.surface_data.sensor_1A.Builder newBuilder(schemas.surface_data.sensor_1A.Builder other) {
    return new schemas.surface_data.sensor_1A.Builder(other);
  }
  
  /**
   * Creates a new sensor_1A RecordBuilder by copying an existing sensor_1A instance.
   * @param other The existing instance to copy.
   * @return A new sensor_1A RecordBuilder
   */
  public static schemas.surface_data.sensor_1A.Builder newBuilder(schemas.surface_data.sensor_1A other) {
    return new schemas.surface_data.sensor_1A.Builder(other);
  }
  
  /**
   * RecordBuilder for sensor_1A instances.
   */
  public static class Builder extends org.apache.avro.specific.SpecificRecordBuilderBase<sensor_1A>
    implements org.apache.avro.data.RecordBuilder<sensor_1A> {

    private java.lang.CharSequence timestamp;
    private java.lang.CharSequence serial_number;
    private java.util.List<java.lang.Double> datapoints;

    /** Creates a new Builder */
    private Builder() {
      super(schemas.surface_data.sensor_1A.SCHEMA$);
    }
    
    /**
     * Creates a Builder by copying an existing Builder.
     * @param other The existing Builder to copy.
     */
    private Builder(schemas.surface_data.sensor_1A.Builder other) {
      super(other);
      if (isValidValue(fields()[0], other.timestamp)) {
        this.timestamp = data().deepCopy(fields()[0].schema(), other.timestamp);
        fieldSetFlags()[0] = true;
      }
      if (isValidValue(fields()[1], other.serial_number)) {
        this.serial_number = data().deepCopy(fields()[1].schema(), other.serial_number);
        fieldSetFlags()[1] = true;
      }
      if (isValidValue(fields()[2], other.datapoints)) {
        this.datapoints = data().deepCopy(fields()[2].schema(), other.datapoints);
        fieldSetFlags()[2] = true;
      }
    }
    
    /**
     * Creates a Builder by copying an existing sensor_1A instance
     * @param other The existing instance to copy.
     */
    private Builder(schemas.surface_data.sensor_1A other) {
            super(schemas.surface_data.sensor_1A.SCHEMA$);
      if (isValidValue(fields()[0], other.timestamp)) {
        this.timestamp = data().deepCopy(fields()[0].schema(), other.timestamp);
        fieldSetFlags()[0] = true;
      }
      if (isValidValue(fields()[1], other.serial_number)) {
        this.serial_number = data().deepCopy(fields()[1].schema(), other.serial_number);
        fieldSetFlags()[1] = true;
      }
      if (isValidValue(fields()[2], other.datapoints)) {
        this.datapoints = data().deepCopy(fields()[2].schema(), other.datapoints);
        fieldSetFlags()[2] = true;
      }
    }

    /**
      * Gets the value of the 'timestamp' field.
      * @return The value.
      */
    public java.lang.CharSequence getTimestamp() {
      return timestamp;
    }

    /**
      * Sets the value of the 'timestamp' field.
      * @param value The value of 'timestamp'.
      * @return This builder.
      */
    public schemas.surface_data.sensor_1A.Builder setTimestamp(java.lang.CharSequence value) {
      validate(fields()[0], value);
      this.timestamp = value;
      fieldSetFlags()[0] = true;
      return this; 
    }

    /**
      * Checks whether the 'timestamp' field has been set.
      * @return True if the 'timestamp' field has been set, false otherwise.
      */
    public boolean hasTimestamp() {
      return fieldSetFlags()[0];
    }


    /**
      * Clears the value of the 'timestamp' field.
      * @return This builder.
      */
    public schemas.surface_data.sensor_1A.Builder clearTimestamp() {
      timestamp = null;
      fieldSetFlags()[0] = false;
      return this;
    }

    /**
      * Gets the value of the 'serial_number' field.
      * @return The value.
      */
    public java.lang.CharSequence getSerialNumber() {
      return serial_number;
    }

    /**
      * Sets the value of the 'serial_number' field.
      * @param value The value of 'serial_number'.
      * @return This builder.
      */
    public schemas.surface_data.sensor_1A.Builder setSerialNumber(java.lang.CharSequence value) {
      validate(fields()[1], value);
      this.serial_number = value;
      fieldSetFlags()[1] = true;
      return this; 
    }

    /**
      * Checks whether the 'serial_number' field has been set.
      * @return True if the 'serial_number' field has been set, false otherwise.
      */
    public boolean hasSerialNumber() {
      return fieldSetFlags()[1];
    }


    /**
      * Clears the value of the 'serial_number' field.
      * @return This builder.
      */
    public schemas.surface_data.sensor_1A.Builder clearSerialNumber() {
      serial_number = null;
      fieldSetFlags()[1] = false;
      return this;
    }

    /**
      * Gets the value of the 'datapoints' field.
      * @return The value.
      */
    public java.util.List<java.lang.Double> getDatapoints() {
      return datapoints;
    }

    /**
      * Sets the value of the 'datapoints' field.
      * @param value The value of 'datapoints'.
      * @return This builder.
      */
    public schemas.surface_data.sensor_1A.Builder setDatapoints(java.util.List<java.lang.Double> value) {
      validate(fields()[2], value);
      this.datapoints = value;
      fieldSetFlags()[2] = true;
      return this; 
    }

    /**
      * Checks whether the 'datapoints' field has been set.
      * @return True if the 'datapoints' field has been set, false otherwise.
      */
    public boolean hasDatapoints() {
      return fieldSetFlags()[2];
    }


    /**
      * Clears the value of the 'datapoints' field.
      * @return This builder.
      */
    public schemas.surface_data.sensor_1A.Builder clearDatapoints() {
      datapoints = null;
      fieldSetFlags()[2] = false;
      return this;
    }

    @Override
    public sensor_1A build() {
      try {
        sensor_1A record = new sensor_1A();
        record.timestamp = fieldSetFlags()[0] ? this.timestamp : (java.lang.CharSequence) defaultValue(fields()[0]);
        record.serial_number = fieldSetFlags()[1] ? this.serial_number : (java.lang.CharSequence) defaultValue(fields()[1]);
        record.datapoints = fieldSetFlags()[2] ? this.datapoints : (java.util.List<java.lang.Double>) defaultValue(fields()[2]);
        return record;
      } catch (Exception e) {
        throw new org.apache.avro.AvroRuntimeException(e);
      }
    }
  }

  private static final org.apache.avro.io.DatumWriter
    WRITER$ = new org.apache.avro.specific.SpecificDatumWriter(SCHEMA$);  

  @Override public void writeExternal(java.io.ObjectOutput out)
    throws java.io.IOException {
    WRITER$.write(this, org.apache.avro.specific.SpecificData.getEncoder(out));
  }

  private static final org.apache.avro.io.DatumReader
    READER$ = new org.apache.avro.specific.SpecificDatumReader(SCHEMA$);  

  @Override public void readExternal(java.io.ObjectInput in)
    throws java.io.IOException {
    READER$.read(this, org.apache.avro.specific.SpecificData.getDecoder(in));
  }

}
