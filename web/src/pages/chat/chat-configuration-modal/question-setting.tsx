import { DeleteOutlined, QuestionCircleOutlined } from '@ant-design/icons';
import { Button, Col, Row, Switch, Table, TableProps, Tooltip } from 'antd';
import classNames from 'classnames';
import { useEffect, useState } from 'react';
import { v4 as uuid } from 'uuid';
import { ISegmentedContentProps } from '../interface';
import { EditableCell, EditableRow } from './editable-cell';

import {
  useCreateRecommendQuestion,
  useDeleteRecommendQuestion,
  useFetchRecommendQuestions,
  useUpdateRecommendQuestion,
} from '@/hooks/chat-hooks';
import { useTranslate } from '@/hooks/common-hooks';
import styles from './index.less';

interface DataType {
  key: string;
  question: string;
  valid: boolean;
  new: boolean;
}

const QuestionSetting = ({
  show,
  dialogId,
}: ISegmentedContentProps & {
  dialogId: string;
}) => {
  const [recommendQuestion, setRecommendQuestion] = useState<DataType[]>([]);
  const { fetchRecommendQuestions } = useFetchRecommendQuestions();
  const { createRecommendQuestion } = useCreateRecommendQuestion();
  const { deleteRecommendQuestion } = useDeleteRecommendQuestion();
  const { updateRecommendQuestion } = useUpdateRecommendQuestion();

  const { t } = useTranslate('chat');

  const components = {
    body: {
      row: EditableRow,
      cell: EditableCell,
    },
  };

  const handleRemove = (key: string) => async () => {
    const newData = recommendQuestion.filter((item) => item.key !== key);
    setRecommendQuestion(newData);
    try {
      const data = await deleteRecommendQuestion(key);
      console.log('Question deleted successfully:', data);
      // Optionally, you can update the state or UI here based on the response
    } catch (error) {
      console.error('Failed to delete question:', error);
      // Optionally, you can update the state or UI here to show an error message
    }
  };

  const handleSave = async (row: DataType) => {
    const newData = [...recommendQuestion];
    const index = newData.findIndex((item) => row.key === item.key);
    const item = newData[index];
    newData.splice(index, 1, {
      ...item,
      ...row,
    });
    setRecommendQuestion(newData);
    if (row.new) {
      try {
        const data = await createRecommendQuestion({
          id: row.key,
          question: row.question,
          app_code: dialogId,
        });
        console.log('Question created successfully:', data);
        // Optionally, you can update the state or UI here based on the response
      } catch (error) {
        console.error('Failed to create question:', error);
        // Optionally, you can update the state or UI here to show an error message
      }
    } else {
      try {
        const data = await updateRecommendQuestion({
          id: row.key,
          question: row.question,
        });
        console.log('Question created successfully:', data);
        // Optionally, you can update the state or UI here based on the response
      } catch (error) {
        console.error('Failed to create question:', error);
        // Optionally, you can update the state or UI here to show an error message
      }
    }
  };

  const handleAdd = () => {
    setRecommendQuestion((state: DataType[]) => [
      ...state,
      {
        key: uuid().replace(/-/g, ''),
        question: '',
        valid: true, // Add valid property
        new: true,
      },
    ]);
  };

  const handleVaildChange = (row: DataType) => async (checked: boolean) => {
    const newData = [...recommendQuestion];
    const index = newData.findIndex((item) => row.key === item.key);
    const item = newData[index];
    newData.splice(index, 1, {
      ...item,
      valid: checked,
    });
    setRecommendQuestion(newData);
    const valid = checked ? 'Y' : 'N';
    try {
      const data = await updateRecommendQuestion({
        id: row.key,
        valid: valid,
      });
      console.log('Question created successfully:', data);
      // Optionally, you can update the state or UI here based on the response
    } catch (error) {
      console.error('Failed to create question:', error);
      // Optionally, you can update the state or UI here to show an error message
    }
  };

  const columns: TableProps<DataType>['columns'] = [
    {
      title: t('question'),
      dataIndex: 'question',
      key: 'question',
      onCell: (record: DataType) => ({
        record,
        editable: true,
        dataIndex: 'question',
        title: 'question',
        handleSave,
      }),
    },
    {
      title: t('vaild'),
      dataIndex: 'vaild',
      key: 'vaild',
      width: 40,
      align: 'center',
      render(text, record) {
        return (
          <Switch
            size="small"
            checked={record.valid}
            onChange={handleVaildChange(record)}
          />
        );
      },
    },
    {
      title: t('operation'),
      dataIndex: 'operation',
      width: 30,
      key: 'operation',
      align: 'center',
      render(_, record) {
        return <DeleteOutlined onClick={handleRemove(record.key)} />;
      },
    },
  ];

  useEffect(() => {
    const initializeQuestions = async () => {
      if (!dialogId) return;

      try {
        const data = await fetchRecommendQuestions(dialogId);
        const filteredData = data[0]
          .filter((item: any) => item.question.trim() !== '')
          .map((item: any) => ({
            key: item.id,
            question: item.question,
            valid: item.valid,
            new: false,
          }));
        setRecommendQuestion(filteredData);
      } catch (error) {
        console.error('Error fetching recommend questions:', error);
      }
    };
    initializeQuestions();
  }, [dialogId, fetchRecommendQuestions]);

  return (
    <section
      className={classNames({
        [styles.segmentedHidden]: !show,
      })}
    >
      <section className={classNames(styles.variableContainer)}>
        <Row align={'middle'} justify="end">
          <Col span={9} className={styles.variableAlign}>
            <label className={styles.variableLabel}>
              {t('recommendquestion')}
              <Tooltip title={t('variableTip')}>
                <QuestionCircleOutlined className={styles.variableIcon} />
              </Tooltip>
            </label>
          </Col>
          <Col span={15} className={styles.variableAlign}>
            <Button size="small" onClick={handleAdd}>
              {t('add')}
            </Button>
          </Col>
        </Row>
        {recommendQuestion.length > 0 && (
          <Row>
            <Col span={7}> </Col>
            <Col span={17}>
              <Table
                dataSource={recommendQuestion}
                columns={columns}
                rowKey={'key'}
                className={styles.variableTable}
                components={components}
                rowClassName={() => styles.editableRow}
              />
            </Col>
          </Row>
        )}
      </section>
    </section>
  );
};

export default QuestionSetting;
